from llava import ModelRunner
from teamcraft.utils.env_utils import NpEncoder, process_llava_output, find_closest_previous_time, concatenate_images_pure, extract_png_names, update_coordinates, filter_voxel
from teamcraft.utils.env_utils import get_initial_inp, get_middle_inp, get_initial_inp_dec, get_middle_inp_dec
from teamcraft.utils.demo_utils import TimeoutException, timeout_handler, process_json_files
# Utils
import argparse
import signal
import time

# Timeout
timeout_duration = 300  # seconds
signal.signal(signal.SIGALRM, timeout_handler)


def evaluate(mode, ckpt, tasks, var_low, var_high, mc_port, mineflayer_port, out_folder, load_4bit, load_8bit):
    llava = ModelRunner(model_path = ckpt, load_4bit = load_4bit, load_8bit = load_8bit)
    for env_name in tasks:
        if env_name=='build':
            from teamcraft import BuildEnv as Env
        elif env_name=='break':
            from teamcraft import BreakEnv as Env
        elif env_name=='farm':
            from teamcraft import FarmEnv as Env
        elif env_name=='smelt':
            from teamcraft import SmeltEnv as Env
        
        out_folder_task = out_folder + env_name
        env = Env(output_folder = out_folder_task, mc_port = mc_port, mineflayer_port = mineflayer_port)
        
        for t in range(var_low, var_high):
            # Set alarm for time out
            signal.alarm(timeout_duration)
        
            try:
                # Reset environment
                reset_info = env.reset(t)
                # Get concatenated task image
                concatenate_images = concatenate_images_pure(reset_info[0])
                # Initial state
                images, state, inventory, done, reward = reset_info[1]
                
                if mode == "cen":
                    # Get initial prompt
                    inp_initial = get_initial_inp(env_name, inventory, env)
                    inp_list = []
                    inp_list.append(inp_initial)
                    
                    # Action loop
                    for _ in range(env.action_length*2):
                        # First prespective images for all action bots
                        images = [images[key] for key in env.bot_list]
                        image_input = [concatenate_images]+images
                        
                        # Run model
                        llava_output = llava.run_once(inp_list, images=image_input)
                        actions = process_llava_output(llava_output, env.center_position)
                        
                        # Step action
                        images, state, inventory, done, reward = env.step(actions)
                        
                        # Record history
                        inp_list.append(llava_output.strip('<s>').strip('</s>'))
                        new_inp = get_middle_inp(env_name, inventory, env)
                        inp_list.append(new_inp)
                        
                        print(f"Current reward for task {env_name}, variant {t} is {reward}", "task is done" if done else "")
                        
                        if done:
                            break

                else:
                    # Get initial prompt for each bot
                    inp_list = []
                    for a in env.bot_list:
                        inp_initial = get_initial_inp_dec(env_name, inventory, env, a)
                        inp_list.append([inp_initial])
                        
                    # Action loop
                    for _ in range(env.action_length*2):
                        actions = []
                        for i_a,a in enumerate(env.bot_list):
                            
                            # First prespective images for current action bot
                            images_a = [images[a]]
                            image_input = [concatenate_images] + images_a
                            
                            # Run model
                            llava_output = llava.run_once(inp_list[i_a], images=image_input)
                            actions += process_llava_output(llava_output, env.center_position)
                            
                            # Record history
                            inp_list[i_a].append(llava_output.strip('<s>').strip('</s>'))
                            new_inp = get_middle_inp_dec(env_name,inventory, env, a, i_a)
                            inp_list[i_a].append(new_inp)
                            
                        # Step actions for all action bots
                        images, state, inventory, done, reward = env.step(actions)
                        
                        print(f"Current reward for task {env_name}, variant {t} is {reward}", "task is done" if done else "")
                        
                        if done:
                            break
                
                print(f"Task {env_name} variant {t} completed with no issue.")
                print("----------------------------------------------------------------------------")
            except TimeoutException:
                print(f"Task {env_name} variant {t} timed out in {timeout_duration} seconds.")
                print("----------------------------------------------------------------------------")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                env.env = None
                time.sleep(10)
                print("----------------------------------------------------------------------------")
            finally:
                # Disable alarm after code completes or fails
                signal.alarm(0)

        env.close()
        folder_path = out_folder_task + '/json/'
        eval_set = {'build':['test','shape','material','scene','agents'],
                    'break':['test','shape','material','scene','agents'],
                    'farm':['test','none','crop','scene','agents'],
                    'smelt':['test','goal','furnace','scene','agents'],
                    }
        
        # aggregate results for full evaluation of a task
        if var_high == 250 and var_low == 0:
            for i_t in range(5):
                start_index = i_t * 50
                end_index = (i_t + 1) * 50 - 1
                average_reward, done_true_percentage = process_json_files(folder_path, start_index, end_index)
                print("average reward and success percentage of " + out_folder_task + ' ' + eval_set[env_name][i_t], average_reward, done_true_percentage)
        
        time.sleep(10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to evaluate a checkpoint")

    parser.add_argument("--mode", type=str, default="cen", help="Evaluation mode, could be cen (centralized) or dec (decentralized)")
    parser.add_argument("--ckpt", type=str, default="teamcraft/TeamCraft-VLA-7B-Cen", help="Local path or huggingface name of the checkpoint")
    parser.add_argument("--mc_port", type=int, default=2037, help="Minecraft server port")
    parser.add_argument("--tasks", nargs='+', type=str, default=['build','break','farm','smelt'], help="Task names, could be build, break, farm, or smelt")
    parser.add_argument("--var_low", type=int, default=0, help="Lowest task variant seed, could be 0 to 249")
    parser.add_argument("--var_high", type=int, default=1, help="One above the largest task variant seed, could be 1 to 250")
    parser.add_argument("--mineflayer_port", type=int, default=3000, help="Mineflayer server port")
    parser.add_argument("--out_folder", type=str, default="eval_cen/", help="Output folder path")
    parser.add_argument("--load_4bit", type=bool, default=False, help="Whether to load the checkpoint with 4 bit")
    parser.add_argument("--load_8bit", type=bool, default=False, help="Whether to load the checkpoint with 8 bit")

    args = parser.parse_args()
    assert args.var_high > args.var_low, "var_high should be greater than var_low"
    assert args.mode in ["cen", "dec"], "mode should be either cen or dec"
    print("Evaluating the tasks: %s" % args.tasks)
    print("Evaluating the variants: [%s, %s)" % (args.var_low, args.var_high))
    evaluate(args.mode, args.ckpt, args.tasks, args.var_low, args.var_high, args.mc_port, args.mineflayer_port, args.out_folder, args.load_4bit, args.load_8bit)
