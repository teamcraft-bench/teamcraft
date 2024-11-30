from datetime import datetime
from PIL import Image
import numpy as np
import copy
import time
import json
import math
import os
import re
from skimage.transform import resize
import imageio


def extract_obs(events):
    ret = {}
    for key, value in events.items():
            ret[key] = {
            "voxels": value[-1][1]["voxels"] if "voxels" in value[-1][1] else None,
            "status": value[-1][1]["status"] if "status" in value[-1][1] else None,
            "inventory": value[-1][1]["inventory"] if "inventory" in value[-1][1] else None,
            "nearbyChests": value[-1][1]["nearbyChests"] if "nearbyChests" in value[-1][1] else None,
            "blockRecords": value[-1][1]["blockRecords"] if "blockRecords" in value[-1][1] else None,
            "nearbyFurnaces": value[-1][1]["nearbyFurnaces"] if "nearbyFurnaces" in value[-1][1] else None,
            "onChat": value[-1][1]["onChat"] if "onChat" in value[-1][1] else None,
            }
    return ret

def filter_voxel(state, place_of_interest):
            state = copy.deepcopy(state)
            for bot in state.keys():
                new_voxel = []
                for item in state[bot]['voxels']:
                    if isinstance(item, list):
                        item[1]['x'] = math.floor(item[1]['x'])
                        item[1]['y'] = math.floor(item[1]['y'])
                        item[1]['z'] = math.floor(item[1]['z'])
                        if  [item[1]['x'], item[1]['y'], item[1]['z']] in place_of_interest:
                            new_voxel.append(item)
                state[bot]['voxels'] = new_voxel
                del state[bot]['blockRecords']
            return state

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)
    
def extract_function_names(calls):
            import re
            function_names = []
            for call in calls:
                match = re.match(r"(\w+)\(", call)
                if match:
                    function_names.append(match.group(1))
            return function_names
        
def construct_action_str(actions):
            action_str = ""
            for i in range(len(actions)):
                action_str += f"await Promise.all([{actions[i]}]);"
            action_str = action_str[:-1]
            return action_str
        
        
def find_closest_previous_time(datetime_list, target_time):
    target_dt = datetime.strptime(target_time, '%Y-%m-%d_%H%M%S%f')
    closest_dt = None
    saved_address=''
    for dt_str in datetime_list:
        modified_dt_str = dt_str[11:]
        parsed_datetime = datetime.strptime(modified_dt_str, '%Y-%m-%d_%H%M%S%f')
        # Format the datetime into the desired format
        dt = parsed_datetime.strftime('%Y-%m-%d_%H%M%S%f')
        dt = datetime.strptime(dt, '%Y-%m-%d_%H%M%S%f')
        if dt < target_dt:
            if closest_dt is None or dt > closest_dt:
                closest_dt = dt
                saved_address=dt_str
    return saved_address


def concatenate_images(image_paths, output_path):
    time.sleep(0.5)
    images = [Image.open(image_path) for image_path in image_paths]

    # Assuming all input images are the same size
    image_size = images[0].size
    new_image = Image.new('RGB', (2 * image_size[0], 2 * image_size[1]))

    # Paste images into the new image
    time.sleep(0.5)
    new_image.paste(images[0], (0, 0))
    new_image.paste(images[1], (image_size[0], 0))
    new_image.paste(images[2], (0, image_size[1]))
    if len(images) == 4:
        new_image.paste(images[3], (image_size[0], image_size[1]))

    # Save the concatenated image
    new_image.save(output_path)
    print(f"Concatenated image saved to {output_path}")
    
def concatenate_images_pure(images):
    # time.sleep(0.5)
    # print(images.keys(),'images')
    # print(images.keys(),'key')
    # print(images,'images')
    # images = [images[i] for i in range(3)]
    # images = [Image.open(image_path) for image_path in image_paths]

    # Assuming all input images are the same size
    image_size = images[0]['bot4'].shape
    array1 = images[0]['bot4']
    array2 = images[1]['bot4']
    array3 = images[2]['bot4']
    r1,r2 = image_size[0]//2,image_size[1]//2
    array1_resized = resize(array1, (r1, r2, 3), anti_aliasing=True)
    array2_resized = resize(array2, (r1, r2, 3), anti_aliasing=True)
    array3_resized = resize(array3, (r1, r2, 3), anti_aliasing=True)

    # Create a new array of shape (480, 640, 3) for the output
    output_array = np.zeros((r1*2, r2*2, 3))

    # Place each resized array in its respective quadrant
    output_array[0:r1, 0:r2, :] = array1_resized    # Top-left (0, 0)
    output_array[0:r1, r2:2*r2, :] = array2_resized  # Top-right (0, 1)
    output_array[r1:2*r1, 0:r2, :] = array3_resized  # Bottom-left (1, 0)
    return (output_array * 255).astype(np.uint8)

    # Check the result
    
    

    # Save the output array as an image file
    # imageio.imwrite(output_path, (output_array * 255).astype(np.uint8))

    # print(f"Image saved at {output_path}")
    # print(output_array.shape)
def translate_to_list(input_string):
    # Remove the <s> and </s> tags from the input string
    cleaned_string = input_string.strip('<s>').strip('</s>')
    
    # Split the cleaned string into lines
    lines = cleaned_string.strip().split('\n')
    
    # Convert the list of lines to a list of strings
    result = [line.strip() for line in lines if line.strip()]
    
    return result    

def get_initial_inp(env_name,inventory,env):
    bot_list= env.bot_list
    num_agent = len(bot_list)
    
    
    
    if env_name=='build':
        if num_agent==3:
            v1= "<image>\nThree bots need to build a building on the platform. "
        elif num_agent==2:
            v1= "<image>\nTwo bots need to build a building on the platform. "
        else:
            v1= "<image>\nFour bots need to build a building on the platform. "
    if env_name=='break':
        if num_agent==3:
            v1= "<image>\nThree bots need to break everything on the platform. "
        else:
            v1= "<image>\nTwo bots need to break everything on the platform. "
    if env_name=='farm':
        goal_corp_num = env.done_input[1]
        goal_corp  = env.done_input[0]
        if num_agent==3:
            v1= "<image>\nThree bots need to grow on the platform. "
        else:
            v1= "<image>\nTwo bots need to grow on the platform. "
        v1+="The goal is to get "+str(goal_corp_num)+" " +goal_corp+". "
    if env_name=='smelt':
        count_smelt = str(env.done_input[1])
        goal_smelt  = env.done_input[0]
        introduction = "Cooking Food:\
        1. To cook a 'cooked_beef', I need 'beef'. To get 'beef', I need to kill a 'cow' or a 'mooshroom'.\
        2. To cook a 'cooked_porkchop', I need 'porkchop'. To get 'porkchop', I need to kill a 'pig'.\
        3. To cook a 'cooked_mutton', I need 'mutton'. To get 'mutton', I need to kill a 'sheep'.\
        4. To cook a 'cooked_chicken', I need 'chicken'. To get 'chicken', I need to kill a 'chicken'.\
        5. To cook a 'cooked_rabbit', I need 'rabbit'. To get 'rabbit', I need to kill a 'rabbit'.\
        6. To cook a 'cooked_cod', I need 'cod'.\
        7. To cook a 'cooked_salmon', I need 'salmon'.\
        8. To cook a 'baked_potato', I need a 'potato'.\
        9. To cook a 'dried_kelp', I need a 'kelp'.\
        Crafting Items:\
        1. To craft a 'gold_ingot', I need 'gold_ore'. To get 'gold_ore', I need to obtain 'gold_ore blocks with a pickaxe.\
        2. To craft an 'iron_ingot', I need 'iron_ore'. To get 'iron_ore', I need to obtain 'iron_ore blocks with a pickaxe.\
        3. To craft 'glass', I need 'red_sand'. To get 'red_sand', I need to obtain 'red_sand'.\
        4. To craft 'smooth_sandstone', I need 'sandstone'. To get 'sandstone', I need to obtain 'sandstone' with a pickaxe.\
        5. To craft 'stone', I need 'cobblestone'. To get 'cobblestone', I need to obtain 'cobblestone' with a pickaxe.\
        6. To craft 'sponge', I need 'wet_sponge'. To get 'wet_sponge', I need to obtain 'wet_sponge’.\
        7. To craft 'smooth_quartz', I need 'quartz_block'. To get 'quartz_block', I need to obtain 'quartz_block' with a pickaxe.\
        Fuel Sources:\
        1. To fuel the furnace, I can use 'coal'. To get 'coal', I need to obtain 'coal_ore'.\
        2. To fuel the furnace, I can use 'lava_bucket', 'coal_block', 'charcoal', .\
        3. To fuel the furnace, I can use 'oak_log', 'birch_log', 'acacia_log', 'spruce_log', 'oak_planks', 'birch_planks', 'acacia_planks', or 'spruce_planks'. I can also obtain those blocks.\
        I do not need to get those resource if they already in my inventory."
        
        if num_agent==3:
            v1= "<image>\nThree bots need to craft "+count_smelt+" "+goal_smelt+". here are the instructions: "+ introduction
        else:
            v1= "<image>\nTwo bots need to craft "+count_smelt+" "+goal_smelt+". here are the instructions: "+ introduction
    
    for i_b in range(num_agent):
        b = bot_list[i_b]
        # print(list(data_conf[b]['inventory'].keys()),'list')
        inventory_item=(list(inventory[b].keys()))
        for item in inventory_item:
            v1+=b
            v1+=" has "
            num=inventory[b][item]
            v1+=str(num)
            v1+=" "
            v1+=item
            v1+=". "
    if len(bot_list)==3:
        v1+="Write the actions for bot1, bot2 and bot3 based on this given observation."
    elif len(bot_list)==2:
        v1+="Write the actions for bot1, bot2 based on this given observation."
    else:
        v1+="Write the actions for bot0, bot1, bot2, bot3 based on this given observation."

    return v1

def get_initial_inp_text(env_name,inventory,env,state,json_data):
    bot_list= env.bot_list
    num_agent = len(bot_list)
    
    
    
    if env_name=='build':
        if num_agent==3:
            v1= "Three bots need to build a building on the platform. "
        elif num_agent==2:
            v1= "Two bots need to build a building on the platform. "
        else:
            v1= "Four bots need to build a building on the platform. "
    if env_name=='break':
        if num_agent==3:
            v1= "Three bots need to break everything on the platform. "
        else:
            v1= "Two bots need to break everything on the platform. "
    if env_name=='farm':
        goal_corp_num = env.done_input[1]
        goal_corp  = env.done_input[0]
        if num_agent==3:
            v1= "Three bots need to grow on the platform. "
        else:
            v1= "Two bots need to grow on the platform. "
        v1+="The goal is to get "+str(goal_corp_num)+" " +goal_corp+". "
    if env_name=='smelt':
        count_smelt = str(env.done_input[1])
        goal_smelt  = env.done_input[0]
        introduction = "Cooking Food:\
        1. To cook a 'cooked_beef', I need 'beef'. To get 'beef', I need to kill a 'cow' or a 'mooshroom'.\
        2. To cook a 'cooked_porkchop', I need 'porkchop'. To get 'porkchop', I need to kill a 'pig'.\
        3. To cook a 'cooked_mutton', I need 'mutton'. To get 'mutton', I need to kill a 'sheep'.\
        4. To cook a 'cooked_chicken', I need 'chicken'. To get 'chicken', I need to kill a 'chicken'.\
        5. To cook a 'cooked_rabbit', I need 'rabbit'. To get 'rabbit', I need to kill a 'rabbit'.\
        6. To cook a 'cooked_cod', I need 'cod'.\
        7. To cook a 'cooked_salmon', I need 'salmon'.\
        8. To cook a 'baked_potato', I need a 'potato'.\
        9. To cook a 'dried_kelp', I need a 'kelp'.\
        Crafting Items:\
        1. To craft a 'gold_ingot', I need 'gold_ore'. To get 'gold_ore', I need to obtain 'gold_ore blocks with a pickaxe.\
        2. To craft an 'iron_ingot', I need 'iron_ore'. To get 'iron_ore', I need to obtain 'iron_ore blocks with a pickaxe.\
        3. To craft 'glass', I need 'red_sand'. To get 'red_sand', I need to obtain 'red_sand'.\
        4. To craft 'smooth_sandstone', I need 'sandstone'. To get 'sandstone', I need to obtain 'sandstone' with a pickaxe.\
        5. To craft 'stone', I need 'cobblestone'. To get 'cobblestone', I need to obtain 'cobblestone' with a pickaxe.\
        6. To craft 'sponge', I need 'wet_sponge'. To get 'wet_sponge', I need to obtain 'wet_sponge’.\
        7. To craft 'smooth_quartz', I need 'quartz_block'. To get 'quartz_block', I need to obtain 'quartz_block' with a pickaxe.\
        Fuel Sources:\
        1. To fuel the furnace, I can use 'coal'. To get 'coal', I need to obtain 'coal_ore'.\
        2. To fuel the furnace, I can use 'lava_bucket', 'coal_block', 'charcoal', .\
        3. To fuel the furnace, I can use 'oak_log', 'birch_log', 'acacia_log', 'spruce_log', 'oak_planks', 'birch_planks', 'acacia_planks', or 'spruce_planks'. I can also obtain those blocks.\
        I do not need to get those resource if they already in my inventory."
        
        if num_agent==3:
            v1= "Three bots need to craft "+count_smelt+" "+goal_smelt+". here are the instructions: "+ introduction
        else:
            v1= "Two bots need to craft "+count_smelt+" "+goal_smelt+". here are the instructions: "+ introduction
    
    a1,b1,c1 = env.center_position
    if env_name=='smelt' or env_name=='break':
        # [a1,b1,c1] = json_data["center_position"]
        for item in state['bot1']['voxels']:
            v1+= item[0]+" is on ["+str(item[1]['x']-a1)+" ,"+str(item[1]['y']-b1)+" ,"+str(item[1]['z']-c1)+"]. "
    
    elif env_name=='build':
        # [a1,b1,c1] = json_data["center_position"]
        v5 = "Target building is: {"
        for item in json_data["done_input"]:
            v5+='Put ' +item[0]+" on [" +str(item[1]-a1)+" ,"+str(item[2]-b1)+" ,"+str(item[3]-c1)+"]. "
        v5+="}. "
        v1+=v5
    else:
        # a1,b1,c1 = env.center_position
        for item in state['bot1']['voxels']:
            if len(item)==2:
                v1+= item[0]+" is on ["+str(item[1]['x']-a1)+" ,"+str(item[1]['y']-b1)+" ,"+str(item[1]['z']-c1)+"]. "
            elif len(item)==3:
                v1+= item[0]+" is on ["+str(item[1]['x']-a1)+" ,"+str(item[1]['y']-b1)+" ,"+str(item[1]['z']-c1)+"] with value of "+str(item[2])+". "
        
        
    
    for i_b in range(num_agent):
        b = bot_list[i_b]
        # print(list(data_conf[b]['inventory'].keys()),'list')
        inventory_item=(list(inventory[b].keys()))
        for item in inventory_item:
            v1+=b
            v1+=" has "
            num=inventory[b][item]
            v1+=str(num)
            v1+=" "
            v1+=item
            v1+=". "
    if len(bot_list)==3:
        v1+="Write the actions for bot1, bot2 and bot3 based on this given observation."
    elif len(bot_list)==2:
        v1+="Write the actions for bot1, bot2 based on this given observation."
    else:
        v1+="Write the actions for bot0, bot1, bot2, bot3 based on this given observation."

    return v1

def get_initial_inp_dec(env_name,inventory,env,a):
    bot_list= env.bot_list
    num_agent = len(bot_list)
    
    
    
    if env_name=='build':
        if num_agent==3:
            v1= "<image>\nThree bots need to build a building on the platform. "
        elif num_agent==2:
            v1= "<image>\nTwo bots need to build a building on the platform. "
        else:
            v1= "<image>\nFour bots need to build a building on the platform. "
    if env_name=='break':
        if num_agent==3:
            v1= "<image>\nThree bots need to break everything on the platform. "
        else:
            v1= "<image>\nTwo bots need to break everything on the platform. "
    if env_name=='farm':
        goal_corp_num = env.done_input[1]
        goal_corp  = env.done_input[0]
        if num_agent==3:
            v1= "<image>\nThree bots need to grow on the platform. "
        else:
            v1= "<image>\nTwo bots need to grow on the platform. "
        v1+="The goal is to get "+str(goal_corp_num)+" " +goal_corp+". "
    if env_name=='smelt':
        count_smelt = str(env.done_input[1])
        goal_smelt  = env.done_input[0]
        introduction = "Cooking Food:\
        1. To cook a 'cooked_beef', I need 'beef'. To get 'beef', I need to kill a 'cow' or a 'mooshroom'.\
        2. To cook a 'cooked_porkchop', I need 'porkchop'. To get 'porkchop', I need to kill a 'pig'.\
        3. To cook a 'cooked_mutton', I need 'mutton'. To get 'mutton', I need to kill a 'sheep'.\
        4. To cook a 'cooked_chicken', I need 'chicken'. To get 'chicken', I need to kill a 'chicken'.\
        5. To cook a 'cooked_rabbit', I need 'rabbit'. To get 'rabbit', I need to kill a 'rabbit'.\
        6. To cook a 'cooked_cod', I need 'cod'.\
        7. To cook a 'cooked_salmon', I need 'salmon'.\
        8. To cook a 'baked_potato', I need a 'potato'.\
        9. To cook a 'dried_kelp', I need a 'kelp'.\
        Crafting Items:\
        1. To craft a 'gold_ingot', I need 'gold_ore'. To get 'gold_ore', I need to obtain 'gold_ore blocks with a pickaxe.\
        2. To craft an 'iron_ingot', I need 'iron_ore'. To get 'iron_ore', I need to obtain 'iron_ore blocks with a pickaxe.\
        3. To craft 'glass', I need 'red_sand'. To get 'red_sand', I need to obtain 'red_sand'.\
        4. To craft 'smooth_sandstone', I need 'sandstone'. To get 'sandstone', I need to obtain 'sandstone' with a pickaxe.\
        5. To craft 'stone', I need 'cobblestone'. To get 'cobblestone', I need to obtain 'cobblestone' with a pickaxe.\
        6. To craft 'sponge', I need 'wet_sponge'. To get 'wet_sponge', I need to obtain 'wet_sponge’.\
        7. To craft 'smooth_quartz', I need 'quartz_block'. To get 'quartz_block', I need to obtain 'quartz_block' with a pickaxe.\
        Fuel Sources:\
        1. To fuel the furnace, I can use 'coal'. To get 'coal', I need to obtain 'coal_ore'.\
        2. To fuel the furnace, I can use 'lava_bucket', 'coal_block', 'charcoal', .\
        3. To fuel the furnace, I can use 'oak_log', 'birch_log', 'acacia_log', 'spruce_log', 'oak_planks', 'birch_planks', 'acacia_planks', or 'spruce_planks'. I can also obtain those blocks.\
        I do not need to get those resource if they already in my inventory."
        
        if num_agent==3:
            v1= "<image>\nThree bots need to craft "+count_smelt+" "+goal_smelt+". here are the introductions: "+ introduction
        else:
            v1= "<image>\nTwo bots need to craft "+count_smelt+" "+goal_smelt+". here are the introductions: "+ introduction
    
    for i_b in range(num_agent):
        b = bot_list[i_b]
        # print(list(data_conf[b]['inventory'].keys()),'list')
        inventory_item=(list(inventory[b].keys()))
        for item in inventory_item:
            v1+=b
            v1+=" has "
            num=inventory[b][item]
            v1+=str(num)
            v1+=" "
            v1+=item
            v1+=". "
    
    v1+="Write the actions for "+a+" based on this given observation."

    return v1


def get_middle_inp_dec(env_name,inventory,env,a,i_a):
    bot_list= env.bot_list
    num_agent = len(bot_list)
    v1=""
    # if env_name=='build':
        
            
    if env_name=='smelt' or env_name=='farm':
        b = a
        # print(list(data_conf[b]['inventory'].keys()),'list')
        inventory_item=(list(inventory[b].keys()))
        for item in inventory_item:
            v1+=b
            v1+=" has "
            num=inventory[b][item]
            v1+=str(num)
            v1+=" "
            v1+=item
            v1+=". "
    
    v1+="Write the actions for "+a+" based on this given observation."


    return v1

def get_middle_inp(env_name,inventory,env):
    bot_list= env.bot_list
    num_agent = len(bot_list)
    v1=""
    # if env_name=='build':
        
            
    if env_name=='smelt' or env_name=='farm':
        for i_b in range(num_agent):
            b = bot_list[i_b]
            # print(list(data_conf[b]['inventory'].keys()),'list')
            inventory_item=(list(inventory[b].keys()))
            for item in inventory_item:
                v1+=b
                v1+=" has "
                num=inventory[b][item]
                v1+=str(num)
                v1+=" "
                v1+=item
                v1+=". "
    if len(bot_list)==3:
        v1+="Write the actions for bot1, bot2 and bot3 based on this given observation."
    elif len(bot_list)==2:
        v1+="Write the actions for bot1, bot2 based on this given observation."
    else:
        v1+="Write the actions for bot0, bot1, bot2, bot3 based on this given observation."


    return v1


def get_middle_inp_text(env_name,inventory,env,state,json_data):
    bot_list= env.bot_list
    num_agent = len(bot_list)
    a1,b1,c1 = env.center_position
    v1=""
    if env_name=='build':
        v5 = "Target building is: {"
        for item in json_data["done_input"]:
            v5+='Put ' +item[0]+" on [" +str(item[1]-a1)+" ,"+str(item[2]-b1)+" ,"+str(item[3]-c1)+"]. "
        v5+="}. "
        v1+=v5
        
            
    # if env_name=='smelt' or env_name=='farm':
    for i_b in range(num_agent):
        b = bot_list[i_b]
        # print(list(data_conf[b]['inventory'].keys()),'list')
        inventory_item=(list(inventory[b].keys()))
        for item in inventory_item:
            v1+=b
            v1+=" has "
            num=inventory[b][item]
            v1+=str(num)
            v1+=" "
            v1+=item
            v1+=". "
    if env_name=='farm':
        for item in state['bot1']['voxels']:
            if len(item)==2:
                v1+= item[0]+" is on ["+str(item[1]['x']-a1)+" ,"+str(item[1]['y']-b1)+" ,"+str(item[1]['z']-c1)+"]. "
            elif len(item)==3:
                v1+= item[0]+" is on ["+str(item[1]['x']-a1)+" ,"+str(item[1]['y']-b1)+" ,"+str(item[1]['z']-c1)+"] with value of "+str(item[2])+". "
        
    else:
        for item in state['bot1']['voxels']:
            v1+= item[0]+" is on ["+str(item[1]['x']-a1)+" ,"+str(item[1]['y']-b1)+" ,"+str(item[1]['z']-c1)+"]. "
    if len(bot_list)==3:
        v1+="Write the actions for bot1, bot2 and bot3 based on this given observation."
    elif len(bot_list)==2:
        v1+="Write the actions for bot1, bot2 based on this given observation."
    else:
        v1+="Write the actions for bot0, bot1, bot2, bot3 based on this given observation."


    return v1




def process_llava_output(output,env_center_position):
    a1,b1,c1 = env_center_position
    action = translate_to_list(output)
    # print(action,'action!!!!!!!!!!!!!')
    a_new =[]
    for a_ in action:
        # print(a_,'a_')
        a_new.append(update_coordinates(a_,a1,b1,c1))
    return a_new

def extract_png_names(folder_path):
    # Initialize an empty list to hold the names without the extension
    names_list = []
    
    # Iterate through the files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file has a .png extension
        if filename.endswith(".png"):
            # Remove the extension and add the name to the list
            name_without_extension = os.path.splitext(filename)[0]
            names_list.append(name_without_extension)
    
    # Return the list of names without the extension
    return names_list
    
# def update_coordinates(input_str,a,b,c):
#     # Regular expression to match the Vec3 coordinates
#     # pattern = r"Vec3\((\d+),(\d+),(\d+)\)"
#     pattern = r"Vec3\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)"
    
#     # Search for the pattern in the input string
#     match = re.search(pattern, input_str)
    
#     if match:
#         # Extract the coordinates as strings
#         x_str, y_str, z_str = match.groups()

        
#         # Convert the coordinates to integers
#         x, y, z = int(x_str), int(y_str), int(z_str)
#         # Perform the arithmetic operations
#         new_x = x - a
#         new_y = y - b
#         new_z = z - c
        
#         # Create the new Vec3 string
#         new_vec3 = f"Vec3({new_x},{new_y},{new_z})"
        
#         # Replace the old Vec3 with the new one in the input string
#         updated_str = re.sub(pattern, new_vec3, input_str)
        
#         return updated_str
#     else:
#         return input_str

def update_coordinates(input_str,a,b,c):
    # Regular expression to match the Vec3 coordinates
    pattern = r"Vec3\((-?\d+),(-?\d+),(-?\d+)\)"
    
    # Search for the pattern in the input string
    match = re.search(pattern, input_str)
    
    if match:
        # print('match',input_str)
        # Extract the coordinates as strings
        x_str, y_str, z_str = match.groups()
        
        # Convert the coordinates to integers
        x, y, z = int(x_str), int(y_str), int(z_str)
        
        # Perform the arithmetic operations
        new_x = x + a
        new_y = y + b
        new_z = z + c
        
        # Create the new Vec3 string
        new_vec3 = f"Vec3({new_x},{new_y},{new_z})"
        
        # Replace the old Vec3 with the new one in the input string
        updated_str = re.sub(pattern, new_vec3, input_str)
        
        return updated_str.replace(",1,",",")
    else:
        print('Warning: coordinate not found, return origin string', input_str)
        return input_str