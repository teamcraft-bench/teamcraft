import argparse
import signal
import time
import json
import os

def process_json_files(folder_path, start=1, end=50):
    total_reward = 0
    total_done_true = 0
    total_files = 0

    for i in range(start, end + 1):
        file_name = f"{i}.json"
        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                data = json.load(file)

                # Filter keys to include only numeric ones and find the last key
                numeric_keys = [key for key in data.keys() if key.isdigit()]
                if not numeric_keys:
                    continue  # Skip if there are no numeric keys

                last_key = max(numeric_keys, key=int)

                last_entry = data[last_key]
                if last_entry.get('reward', 0)>1:
                    total_reward += 1
                else:
                    total_reward += last_entry.get('reward', 0)
                
                total_done_true += 1 if last_entry.get('done', False) else 0
                total_files += 1
    print(total_files,'total files')
    total_files = end-start+1
    average_reward = total_reward / total_files if total_files > 0 else 0
    done_true_percentage = (total_done_true / total_files) * 100 if total_files > 0 else 0

    return average_reward, done_true_percentage


class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Code execution exceeded the time limit")
