import json
import numpy as np
import os
import random
import copy


class NpEncoder(json.JSONEncoder):
    """Custom JSON encoder subclass to handle numpy data types."""

    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def interleave_lists(lists):
    """
    Interleaves elements from a list of lists into a list of sublists, where each sublist contains
    one element from each of the input lists, in order.

    Parameters:
        lists (list of lists): List containing several sublists from which elements are interleaved.

    Returns:
        list: A list of sublists, each containing one element from each input sublist.
    """
    # Ensure all lists are mutable (not necessary unless lists are tuples or other immutable types)
    lists = [list(sublist) for sublist in lists]
    
    combined = []
    # Continue looping until all lists are exhausted
    while any(lists):  # any() is true if at least one list still has items
        sublist = []
        for sublist_index in range(len(lists)):
            if lists[sublist_index]:  # Check if the current sublist has any items left
                sublist.append(lists[sublist_index].pop(0))  # Pop the first element if available
        combined.append(sublist)
    return combined


def translate_to_coordinates(index):
    """Convert a linear index to a 4x4 grid coordinate."""
    return index % 4, index // 4


def initialize_output_directory(path):
    """Ensure the output directory exists; create if it does not."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        
def select_items(item_dict, n_items):
    """
    Selects a random set of items from a given dictionary.

    Parameters:
        item_dict (dict): Dictionary where keys are tool names and values are another dictionary of items.
        n_items (int): Number of random items to select.

    Returns:
        list: List of tuples, each containing a tool and an item.
    """
    items = [(tool, item) for tool, items in item_dict.items() for item in items.keys()]
    return random.choices(items, k=n_items)


def sample_dict_item(dict):
    """Randomly select a key-value pair from a dictionary."""
    key = random.choice(list(dict.keys()))
    return dict[key]

def translate_to_coordinates(spot, width=4, depth=4, height=3):
        """
        Translate a 1D spot index to 3D coordinates.
        """
        z = spot // (width * depth)
        y = (spot % (width * depth)) // width
        x = spot % width
        return x, y, z

def is_block_accessible(x, y, z, grid):
    """
    Check if a block at (x, y, z) is accessible in a 3D grid.
    """
    if z > 0 and grid[x][y][z-1] == 0:
        return False  # No floating blocks allowed
    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for dx, dy, dz in directions:
        nx, ny, nz = x + dx, y + dy, z + dz
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and 0 <= nz < len(grid[0][0]):
            if grid[nx][ny][nz] == 0:
                return True
    return False

def will_block_previous(x, y, z, grid):
    """
    Check if placing a block at (x, y, z) will block any previous placements.
    """
    directions = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    for dx, dy, dz in directions:
        nx, ny, nz = x + dx, y + dy, z + dz
        if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and 0 <= nz < len(grid[0][0]):
            if grid[nx][ny][nz] == 1 and not is_block_accessible(nx, ny, nz, grid):
                return True
    return False

def hide_other(x, y, z, grid, base_shape):
    if base_shape == [2,3,2]:
        if x == 1 and y == 1 and z == 1:
            return True
        if x == 1 and y == 0 and z == 1:
            return True
    if base_shape == [2,2,2]:
        if x == 1 and y == 0 and z == 1:
            return True
    return False
    
    
def translate_to_index(x, y, z, width=4, depth=4, height=3):
    """
    Translate 3D coordinates (x, y, z) back to a 1D spot index.
    """
    return z * (width * depth) + y * width + x


def generate_playground_config(name, center, size=5):
    """
    Generate a configuration dictionary for a playground based on the given parameters.

    Parameters:
    name (str): The name of the playground location.
    center (list[int]): A list containing the x, y, and z coordinates of the center of the playground.
    size (int, optional): The size of the playground in both x and z directions. Default is 5x5.

    Returns:
    dict: A dictionary containing the playground configuration.
    """
    
    x, y, z = center
    half_size = size // 2
    
    config = {
        "name": name,
        "x": [x - half_size, x + half_size],
        "z": [z - half_size, z + half_size],
        "y": y,
        "bot_range": [[x + half_size + 1, x + half_size + 4], [z - half_size + 1, z + half_size + 4], y + 2],
        "center": [x, y, z]
    }
    
    return config
    
    
def generate_multiple_playgrounds(playgrounds):
    """
    Generate a dictionary containing multiple playground configurations.

    Parameters:
    playgrounds (list[tuple]): A list of tuples where each tuple contains a name (str), center (list[int]), 
                               and optional size (int) for the playground.

    Returns:
    dict: A dictionary mapping playground names to their configuration dictionaries.
    """
    return {name: generate_playground_config(name, center, size) for name, center, size in playgrounds}


if __name__ == "__main__":
    
    agent_counts =[2, 3]

    background = ['minecraft:cyan_concrete', 'minecraft:stone', 'minecraft:oak_wood', 'minecraft:hay_block', 'minecraft:glass',
                'minecraft:glowstone', 'minecraft:gold_block', 'minecraft:pink_wool', 'minecraft:obsidian','minecraft:smooth_quartz']

    all_items = ['oak_fence', 'birch_log', 'bookshelf', 'acacia_fence', 'oak_log', 'coal_ore',
                 'bricks', 'sandstone', 'stone', 'iron_ore', 'gold_ore', 'sponge', 'sea_lantern',
                 'dirt', 'grass_block', 'clay', 'oak_planks', 'emerald_block', 'bricks', 'pumpkin',
                 'orange_concrete', 'purple_wool', 'end_stone'
                ]
    
    # name, center, size
    # Recommended size is 5
    playground_data = [
                        ("villege", [223, 70, 128], 5),
                        ("desert_villege", [4261, 74, 161], 5),
                        ("swamp", [4284, 64, 1126], 5),
                        ("ice_on_water", [7393, 63, 5325], 5),
                        ("snow_mountain", [11671, 106, 8488], 5),
                        ("mountain_half", [4302, 97, 211], 5),
                        ("forest", [14140, 67, 10171], 5)
                      ]

    # Shape of the base used for block placement
    # Width, Length, Height
    base_shape = [[4,1,2],[3,1,2], [2,2,2],[2,3,2]]

    
    # ------- Output Configuration --------
    out_dir = '/YOUR_PATH_TO_TASK_FOLDER/configure/'
    initialize_output_directory(out_dir)


    # Batch random generation of JSON files
    for num_action in range(0, 100):

        random.seed(num_action)
        
        var_cfg = {
            "agent_counts": random.sample(agent_counts, 1),
            "background": random.sample(background, 1),
            "playground_location": sample_dict_item(generate_multiple_playgrounds(playground_data)),
            "base_shape": random.sample(base_shape,1),
            "block_type": None, 
            "placement_shape": None}

        # ----- Bot Configuration -----
        bot = [f'bot{i}' for i in range(1, var_cfg["agent_counts"][0]+1)]

        bot_range_x = [var_cfg["playground_location"]["bot_range"][0] for _ in range(len(bot))]
        bot_range_y = [var_cfg["playground_location"]["bot_range"][1] for _ in range(len(bot))]
        bot_height = var_cfg["playground_location"]["bot_range"][2]

        bot_pitch = [[-10,10],[-10,10],[-10,10],[-10,10]]
        bot_yaw = [[0,360],[0,360],[0,360],[0,360]]

        bot_inventory = [[] for _ in range(len(bot))]


        # ----- Command Configuration -----
        input_data = {}
        
        # Example command, for reference
        input_data['command']=f"""
                        await bot1.chat('hello!!!!!!!!!!!');
                        await bot1.chat('/gamerule doMobSpawning false');
                        await bot1.chat('/gamerule randomTickSpeed 0');
                        """
                    
        if len(bot) == 2:
            input_data['command']+="""
                        await bot3.chat('/gamemode spectator');
                        await bot3.chat('/tp @p 10 10 10');
                        """
        if len(bot) == 3 or len(bot) == 4:
            input_data['command']+="""
                        await bot3.chat('/gamemode survival');
                        """
        
        # ------ Playground Configuration ------
        # obs_command should be center and +4 block above the center with playgound size of 5, 
        # IMPORTANT: for a larger playground size, change obs_command and observer setup command accordingly
        # obs_command yaw pitch should be -90 90    
            
        xx, yy, zz = var_cfg['playground_location']['x'][0], var_cfg['playground_location']['y'], var_cfg['playground_location']['z'][0]
        xxx, zzz =   var_cfg['playground_location']['x'][1], var_cfg['playground_location']['z'][1]
        obs_x, obs_y, obs_z = var_cfg['playground_location']['center']
        obs_y += 4
        
        
        input_data['command']+=f"await bot1.chat('/forceload add {xx-1} {zzz+1}');"
        
        # Clear the area
        input_data['command'] += f"await bot1.chat('/fill {xx-4} {yy-1} {zz-4} {xxx+4} {yy+1} {zzz+4} minecraft:air');"
        
        # Set up the observer
        input_data['command']+=f"""
                        await bot4.chat('/setblock {obs_x} {obs_y-1} {obs_z} minecraft:barrier');
                        await bot4.chat('/gamemode spectator');
                        await bot4.chat('/tp @p {obs_x} {obs_y} {obs_z} -90 90');
                    """
        
        # Fill the ground layer with the background material
        input_data['command'] += f"await bot1.chat('/fill {xx} {yy-1} {zz} {xxx} {yy-1} {zzz} {var_cfg['background'][0]}');"

        # Fill the layers above with air
        input_data['command'] += f"await bot1.chat('/fill {xx-1} {yy} {zz-1} {xxx} {yy+1} {zzz} minecraft:air');"
        

        # ----- Observer Configuration -----
        input_data['obs_command'] = []
        
        input_data['obs_command'].append([f"""
                        await bot4.chat('/setblock {obs_x-6} {obs_y-5} {obs_z} minecraft:barrier');
                        await bot4.chat('/tp @p {obs_x-6} {obs_y-4} {obs_z} -90 0');
                    """])
        input_data['obs_command'].append([f"""
                        await bot4.chat('/setblock {obs_x} {obs_y-5} {obs_z+6} minecraft:barrier');
                        await bot4.chat('/tp @p {obs_x} {obs_y-4} {obs_z+6} -180 0');
                    """])
        input_data['obs_command'].append([f"""
                        await bot4.chat('/tp @p {obs_x} {obs_y} {obs_z} -90 90');
                    """])
        
                    
        # ----- Done Input Configuration -----
        
        done_input=[]
         
        input_data['variant']=num_action
        input_data['actions']=[]
        input_data['done_input']=done_input
        
        max_capacity = var_cfg["base_shape"][0][0] * var_cfg["base_shape"][0][1] * 2

            
            
        # ----- Item Configuration -----
        # Target item selection
        n_items = random.randint(6, max_capacity) if len(bot) == 3 else random.randint(5, max_capacity)
        # Randomly pick k items with replacement
        target_item = random.choices(all_items, k=n_items)
        
        var_cfg["block_type"] = target_item
        var_cfg["block_count"] = n_items
        

        # ----- Block Placement Configuration -----
        width, depth, height = var_cfg["base_shape"][0]
        spots = list(range(0, width * depth * height))
        
        
        
        # ----- Example of randomizing placing of "target_item" on the playground ----- 
        
        placed_spots = []
        placed_spots_number = []

        for item in target_item:
            # Randomly select a spot
            spot = spots.pop()
            x, y, z = translate_to_coordinates(spot, width, depth, height)
            
            placed_spots.append((x, z, y))
            placed_spots_number.append(translate_to_index(x, y, z, width, depth, height))
            
            x += var_cfg["playground_location"]["x"][0] + 1
            y += var_cfg["playground_location"]["z"][0] + 1
            z_height = var_cfg['playground_location']["y"] + z
            
            input_data['command'] += f"await bot1.chat('/setblock {x} {z_height} {y} minecraft:{item}');"
            
            # Exapmple done_input. You can design your own done_input based on the reward function
            done_input.append([item,x,z_height,y])
            
            
        var_cfg["placement_shape"] = placed_spots
        var_cfg["placement_shape_number"] = placed_spots_number
        
        
        # ----- Bot Action and Inventory Configuration -----
        # TODO: Implement the bot actions configuration
        action_list = [[] for _ in range(len(bot))]
        # TODO: Implement the bot inventory configuration
        bot_assigned_item = [[] for i in range(len(bot))]
        
        
            
        # ----- Enumearate through the bots and assign actions and inventory -----
        
        for i, b in enumerate(bot):
            input_data[b]={}
            x_min,x_max = bot_range_x[i]
            y_min,y_max = bot_range_y[i]
            pitch_min,pitch_max = bot_pitch[i]
            yaw_min,yaw_max =  bot_yaw[i]
            x = round(random.uniform(x_min, x_max),2)
            y = round(random.uniform(y_min, y_max),2)
            pitch = round(random.uniform(pitch_min, pitch_max),2)
            yaw = round(random.uniform(yaw_min, yaw_max),2)
            input_data[b]['location'] = [x,bot_height,y]
            input_data[b]['rotation'] = [yaw,pitch]
            input_data[b]['inventory'] = {}
            
            input_data['command']+='await '+b+'.chat(\'/tp @p '+str(x)+' '+str(bot_height)+' '+str(y)+' '+str(yaw)+' ' +str(pitch)+' '+'\');'
            for item in bot_assigned_item[i]:
                input_data[b]['inventory'][item]=input_data[b]['inventory'].get(item,0)+random.randint(1, 3)
            for item in random.sample(target_item, random.randint(1, len(target_item))):
                input_data[b]['inventory'][item]=input_data[b]['inventory'].get(item,0)+random.randint(1, 3)
            for item in input_data[b]['inventory']:
                input_data['command']+='await '+b+'.chat(\'/give @p ' +item+' '+str(input_data[b]['inventory'][item])+'\');'

        
        input_data['actions']=interleave_lists(action_list)
        input_data['item_spots']={}
        input_data['variants_config'] = var_cfg
        input_data['bot_list'] = bot
        input_data['center_position'] = var_cfg['playground_location']['center']
        
        # ----- Json file generation --------
        file = out_dir+str(num_action)+'.json'

        with open(file, 'w') as json_file:
            json.dump(input_data, json_file, indent=4, cls=NpEncoder) 
