from teamcraft import teamCraft
from teamcraft.utils import NpEncoder, filter_voxel
from teamcraft.minecraft import MCServerManager
from datetime import datetime, timezone
import gymnasium as gym
import random
import math
import json
import os
    
    
class FarmEnv(gym.Env):
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
        self.task_name = "farm"
        
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
        self.init_goal_inventory_count = json_data['init_goal_inventory_count']
        
        place_of_interest = []
        for i in json_data["variants_config"]["playground_location"]["spot"]:
            place_of_interest.append(i)
            place_of_interest.append([i[0],i[1]+1,i[2]])
        for i in json_data["variants_config"]["playground_location"]["water"]:
            place_of_interest.append(i)
            place_of_interest.append([i[0],i[1]+1,i[2]])
        self.place_of_interest = place_of_interest
        
        farmland_action = json_data["action_obs"][0]
        self.farmland_action = [item for item in farmland_action if not any(keyword in item for keyword in ['wheat', 'potatoes','carrots','beetroots'])]
    
        # ----------- Print config data -----------
        print("Agents count: ", self.bot_count)
        print("Bot list: ", self.bot_list)
        print("Expect action length: ", self.action_length)
        print("Scenes: ", json_data['variants_config']['playground_location']['name'])
        print("Background type: ", json_data['variants_config']['block_type'])
        print("Target type: ", json_data['done_input'][0])
        print("Target count", json_data['done_input'][1])
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
        self.state = None
        self.image = None
        self.voxels = None
        
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
        
        # ------------------- ACTION -------------------
        image, state, inventory, done, reward  = self.step(None)
        info = (image, state, inventory,  done, reward)
        print("reset finished")
        
        return self.task_image, info
        
        
    def calculate_reward(self, bag_item, done_input, init_count):
        total = 0
        for item in bag_item:
            total += item.get(done_input[0], 0)
        return max((total - init_count) / done_input[1] , 0)


    def done_function(self, reward):
        if reward <1:
            return False
        return True


    def step(self, actions):
        if actions is not None:
            print(actions)
            self.observation = self.env.step(code = actions)
            self.actions = actions

            _voxel = [item for item in self.observation['bot1']['voxels'] if isinstance(item, list)]
            corp_action = []
            corps_status =  [[math.floor(item[1]['x']), math.floor(item[1]['y']), math.floor(item[1]['z']), item[2], item[0]] for item in _voxel if item[0] in ['carrots', 'potatoes', 'wheat', 'beetroots']]
            # print(corps_status)
            for i in corps_status:
                if i[4] == 'beetroots':
                    if i[3] == 3:
                        pass
                    else:
                        i[3] += random.randint(1, 3)
                        if i[3] > 3:
                            i[3] = 3
                else:
                    if i[3] == 7:
                        pass
                    else:
                        i[3] += random.randint(3, 7)
                        if i[3] > 7:
                            i[3] = 7
                corp_action.append(f"await bot4.chat('/setblock {i[0]} {i[1]} {i[2]} minecraft:{i[4]}[age={i[3]}]');")
            
            code = "".join(self.farmland_action).join(corp_action)
            # task farm need to look back at middle every timestemp
            for bot_name in self.bot_list:
                code += f"await {bot_name}.lookAt(new Vec3({self.center_position[0]},{self.center_position[1]},{self.center_position[2]}));"
            self.env.step_manuual(code = code)
        
        else:
            self.observation = self.env.step("")
            self.actions = actions
            corp_action = None
        
        
        onChat = [self.observation[a]["onChat"] for a in self.bot_list]
        self.inventory = {a: self.observation[a]["inventory"] for a in self.bot_list}
        _inventory_list = [self.inventory[a] for a in self.bot_list]
        # Note for task farm, voxel used is from bot 1
        self.voxels = [item for item in self.observation['bot1']['voxels'] if isinstance(item, list)]
        self.reward = self.calculate_reward(_inventory_list, self.done_input, self.init_goal_inventory_count)
        self.done = self.done_function(self.reward)
        self.state = filter_voxel(self.observation, self.place_of_interest)
        self.image = self.env.render()
        
        self.metadata[self.time_step]={}
        self.metadata[self.time_step]['time']=datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%S%f')[:-3]  # Truncate microseconds to milliseconds
        self.metadata[self.time_step]['action']=actions
        self.metadata[self.time_step]['state']=self.state
        self.metadata[self.time_step]['done']=self.done
        self.metadata[self.time_step]['reward']=self.reward
        self.metadata[self.time_step]['inventory']=self.inventory
        self.metadata[self.time_step]['farm_setting']=corp_action
        
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

