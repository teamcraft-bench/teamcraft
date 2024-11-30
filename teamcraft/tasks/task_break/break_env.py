from teamcraft import teamCraft
from teamcraft.utils import NpEncoder, filter_voxel
from teamcraft.minecraft import MCServerManager
from datetime import datetime, timezone
import gymnasium as gym
import random
import math
import json
import os


class BreakEnv(gym.Env):
    def __init__(self, 
                 output_folder: str = "./",
                 mc_port: int = 2037, 
                 mineflayer_port: int = 3000) -> None:
        
        self.cwd = os.path.abspath(os.path.dirname(__file__))
        self.mc_port = mc_port
        self.mc_world = None
        self.mc_log = None
        self.mc_server = None
        self.mc_server_thread = None
        self.mineflayer_port = mineflayer_port
        self.mineflayer_log = os.path.join(output_folder, 'logs/')
        self.env = None
        self.task_name = "break"
        
        # init minecraft server
        self.mc_world = os.path.join(self.cwd, f'world_{self.task_name}')
        self.mc_log = os.path.join(output_folder, 'logs/minecraft/')
        if os.path.exists(self.mc_log):
            pass
        else:
            os.makedirs(self.mc_log,exist_ok=True)
        self.mc_server_thread = MCServerManager(self.mc_port, self.mc_world, self.mc_log)
        try:
            self.mc_server_thread.start()
        except Exception as e:
            print(f"An error occurred: {e}")
            
        # init log path
        self.json_file_location = os.path.join(output_folder, 'json/')
        if os.path.exists(self.json_file_location):
            pass
        else:
            os.makedirs(self.json_file_location,exist_ok=True)
            
            
    def reset(self, seed):
        super().reset(seed=seed)
        # ------------------- CLOSE -------------------
        if self.env is not None:
            self.env.close()
            json_file=str(self.seed)+'.json'
            with open(self.json_file_location+json_file,'w') as json_file:
                json.dump(self.metadata, json_file, indent=4, cls = NpEncoder)
                
        if self.mc_server_thread is None and self.env is None:
            raise Exception("Current env has been closed. Please start from the beginning.")
        
        # ------------------- SEED -------------------
        print("\n ------------------- New Variant Started ------------------- \n")
        print("using seed: ", str(seed))
        random.seed(seed)
        
        # ------------------- PATH -------------------
        self.config_path = os.path.join(self.cwd, f'./configure/{str(seed)}.json')
        
        # ----------- Load config data -----------  
        with open(self.config_path, 'r') as file:
            # Load the JSON data
            json_data = json.load(file)
            
        self.seed = seed
        self.init_command = json_data['command']
        self.bot_count = len(json_data["bot_list"])
        self.done_input = json_data['done_input']
        self.action_length = len(json_data['actions'])
        self.bot_list = json_data["bot_list"]
        self.center_position = json_data["center_position"]
        self.obs_command = json_data["obs_command"]
        self.total_block_to_break = len(json_data["variants_config"]["block_type"])
            
        [a1,b1,c1] = self.center_position
        # Note place_of_interest is different in break task
        self.place_of_interest = [[x,y,z] for x in range(a1-3, a1+3) for y in range(b1, b1+4) for z in range(c1-3, c1+3)]
        
        # ----------- Print config data -----------
        print("Agents count: ", self.bot_count)
        print("Bot list: ", self.bot_list)
        print("Expect action length: ", self.action_length)
        print("Scenes: ", json_data['variants_config']['playground_location']['name'])
        print("Background type: ", json_data['variants_config']['background'])
        print("Target type: ", json_data['variants_config']['block_type'])
        print("Target count", len(json_data['variants_config']['block_type']))
        print("Dimensional shapes", json_data['variants_config']['dimension'])
        print("Tool Assignment", json_data['variants_config']['tool_use'])
        print()
        
        # ----------- MAMC environment -----------
        self.env = teamCraft(
                agent_count = self.bot_count,
                mc_port=self.mc_port,
                server_port=self.mineflayer_port,
                env_wait_ticks=20,
                log_path = self.mineflayer_log,
            )
        self.env.start()
        
        # ----------- Init parameter -----------
        self.time_step = 0
        self.actions = []
        self.reward = 0
        self.done = False
        self.task_image = {}
        self.observation = None
        self.metadata = {}
        self.inventory = None
        self.total_placed = 0
        self.total_hit = 0
        self.state = None
        self.image = None
        self.voxels = []
        
        # ----------- First world setup step -----------
        self.observation = self.env.step_manuual(code = self.init_command)
        print('World has been set up')
        
        # ------------------- RECORD -------------------
        code = "await bot4.chat('startRecoding -1 "+ " "+"\');"
        self.env.step_manuual(code = code)
        
        # ------------------- LOOK AT MIDDLE -------------------
        code = ""
        for bot_name in self.bot_list:
            code += f"await {bot_name}.lookAt(new Vec3({self.center_position[0]},{self.center_position[1]},{self.center_position[2]}));"
        self.env.step_manuual(code = code)
        print("all agents now looked at center position")
        
        # ------------------- 3-Views -------------------
        self.metadata['obs'] = {}
        obs_step = 0
        for obs_action in self.obs_command:
            self.metadata['obs'][obs_step]={}
            self.metadata['obs'][obs_step]['time']=datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%S%f')[:-3]
            self.metadata['obs'][obs_step]['action']=obs_action[0]
            self.task_image[obs_step] = self.env.render()
            
            self.env.step_manuual(code = obs_action[0])
            obs_step += 1

        print("orthographic projections observation finished")
        
        # ------------------------------ Break parameters-----------------------------------
        self.item_durability = {}
        self.tool_use = ['stone_axe','stone_pickaxe','stone_shovel','stone_sword']
        self.item_dict_durbility ={
            'bookshelf': ['stone_axe', 2], 'crafting_table': ['stone_axe', 2], 
            'oak_fence': ['stone_axe', 2], 'acacia_fence': ['stone_axe', 2], 
            'oak_log': ['stone_axe', 2], 'birch_log': ['stone_axe', 2], 
            'coal_ore': ['stone_pickaxe', 3], 'bricks': ['stone_pickaxe', 3], 
            'sandstone': ['stone_pickaxe', 3], 'stone': ['stone_pickaxe', 3], 
            'iron_ore': ['stone_pickaxe', 3], 'anvil': ['stone_pickaxe', 3], 
            'dirt': ['stone_shovel', 2], 'sand': ['stone_shovel', 2], 
            'grass_block': ['stone_shovel', 2], 'clay': ['stone_shovel', 2], 
            'cobweb': ['stone_sword', 3], 'gold_ore': ['stone_pickaxe', 3],
            'acacia_log': ['stone_axe', 2]
            }
            
        
        self.bot_tool_list = [[tool for tool in self.tool_use if tool in json_data[bot_name]["inventory"]] for bot_name in self.bot_list]
    
        
        # ------------------- ACTION -------------------
        image, state, inventory, done, reward  = self.step(None)
        info = (image, state, inventory,  done, reward)
        print("reset finished")
        
        return self.task_image, info
        
        
    def done_function(self, voxels, list_loc):
        set_loc = set(list_loc)
        for item in voxels:
            str1 = str(math.floor(item[1]['x']))+'+'+str(math.floor(item[1]['y']))+'+'+str(math.floor(item[1]['z']))
            if str1 in set_loc:
                if item[0]=='air':
                    pass
                else:
                    return False
        return True
    
    
    def reward_function(self, voxels, list_loc, total_block_to_break):
        set_loc = set(list_loc)
        remaining_blocks = 0
        for item in voxels:
            str1 = str(math.floor(item[1]['x']))+'+'+str(math.floor(item[1]['y']))+'+'+str(math.floor(item[1]['z']))
            if str1 in set_loc:
                if not item[0]=='air':
                    remaining_blocks += 1
                    
        return 1 - remaining_blocks / total_block_to_break
    
    
    def translate_action(self, actions, bot_tool_list, item_dict_discrete_new, item_durability, voxels):
        # Creat a item durability dictionary to keep track of how many idential action needed to break a block
        # Only the last action is considered, check if item durability is smaller than 0
        import re
        # Regex pattern to extract the bot name, item name, and coordinates
        pattern = r"mineBlock\((\w+), new Vec3\((-?\d+),(-?\d+),(-?\d+)\)\)"

        return_actions = []
        
        for single_action in actions:
            # Perform the search
            matches = re.search(pattern, single_action)

            if matches:
                bot_name = matches.group(1)
                coordinates = f"{matches.group(2)},{matches.group(3)},{matches.group(4)}"
                item_name = [item[0] for item in voxels if str(math.floor(item[1]['x']))+','+str(math.floor(item[1]['y']))+','+str(math.floor(item[1]['z'])) == coordinates]
                if len(item_name) == 0:
                    print("Invalid coordinates")
                    continue
                else:
                    item_name = item_name[0]
                if item_dict_discrete_new[item_name][0] in bot_tool_list[self.bot_list.index(bot_name)]: # Check if the bot has the tool
                    return_actions.append(single_action)
                else:
                    item_durability[coordinates] = item_durability.get(coordinates, item_dict_discrete_new[item_name][1]) - 1
                    if item_durability[coordinates] <= 0:
                        return_actions.append(single_action)
            else:
                print("Invalid action format")
                return_actions.append('NULL')
        return return_actions
    

    def step(self, actions):
        if actions is not None:
            _inventory_list = [self.inventory[a] for a in self.bot_list]
            print(actions)
            self.observation = self.env.step(code = actions)
            self.actions = actions
            # actions_real = self.translate_action(actions, [[key for key in d.keys()] for d in _inventory_list], self.item_dict_durbility, self.item_durability, self.voxels)
            # self.observation = self.env.step(code = actions_real)
            # self.actions = actions_real
            
            # task break need to look back at center every timestemp
            code = ""
            for bot_name in self.bot_list:
                code += f"await {bot_name}.lookAt(new Vec3({self.center_position[0]},{self.center_position[1]},{self.center_position[2]}));"
            self.env.step_manuual(code = code)
        else:
            self.observation = self.env.step("")
            self.actions = actions
            # actions_real = None
            
        
        onChat = [self.observation[a]["onChat"] for a in self.bot_list]
        self.inventory = {a: self.observation[a]["inventory"] for a in self.bot_list}
        self.voxels = [item for item in self.observation['bot4']['voxels'] if isinstance(item, list)]
        self.reward = self.reward_function(self.voxels, self.done_input, self.total_block_to_break)
        self.done = self.done_function(self.voxels, self.done_input)
        self.state = filter_voxel(self.observation, self.place_of_interest)
        self.image = self.env.render()
        
        self.metadata[self.time_step]={}
        self.metadata[self.time_step]['time']=datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%S%f')[:-3]  # Truncate microseconds to milliseconds
        self.metadata[self.time_step]['action']=actions
        # self.metadata[self.time_step]['action_real']=actions_real
        self.metadata[self.time_step]['state']=self.state
        self.metadata[self.time_step]['done']=self.done
        self.metadata[self.time_step]['reward']=self.reward
        self.metadata[self.time_step]['inventory']=self.inventory
        
        self.time_step +=1
        
        return self.image, self.state, self.inventory, self.done, self.reward
    
    
    def close(self):
        json_file=str(self.seed)+'.json'
        with open(self.json_file_location+json_file,'w') as json_file:
            json.dump(self.metadata, json_file, indent=4, cls = NpEncoder)
        self.env.close()
        self.mc_server_thread.stop()
        self.env = None
        self.mc_server_thread = None
        