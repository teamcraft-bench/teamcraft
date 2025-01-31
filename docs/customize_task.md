# Customizing Your Own Task

To create a custom task, follow these steps:

- Set up a new task environment.
- Generate a configuration file for each task variant.

## Creating a New Task Environment

1. **Clone the Task Template**  
   Copy the `task_build` folder located under `teamcraft/teamcraft/tasks/`, renaming it in the format `task_xxx`.

2. **Rename the Minecraft World Save Folder**  
   Inside `task_xxx`, rename the Minecraft world save folder (`world_build`) to `world_xxx`.

3. **(Optional) Modify the Minecraft World**  
   - Edit `world_xxx` using a local Minecraft instance (refer to [env doc](./env_doc.md) under *Visualization* for setup instructions).  
   - Load `world_xxx` as a game save.
   - Modifed the world using creative mode (Use command `/gamemode creative`)
   - Save the world

4. **Modify the `build_env.py` File**  
   - Rename the `BuildEnv` class following the format `xxxEnv`.
   - Adjust any internal parameters using [env doc](./env_doc.md) as a reference.
   - Modify the `calculate_reward` function:  
     - For block-based rewards, refer to `BreakEnv` and `BuildEnv`.
     - For inventory-based rewards, refer to `FarmEnv` and `SmeltEnv`.
   - Update the `self.done` condition.

5. **Update Import Statements**  
   Modify the following `__init__.py` files to import your environment class:
   - `teamcraft/teamcraft/tasks/task_xxx/__init__.py`
   - `teamcraft/teamcraft/tasks/__init__.py`
   - `teamcraft/teamcraft/__init__.py`



## Generating the Configuration File

1. Follow the instructions in [`config_gen.py`](../config_gen.py), sarting from line 170, to generate the configuration file.
2. Replace the existing `.json` file under `task_xxx/configure` with the new configuration.

## Run
Once completed, you can import and use your custom class with:

```python
from teamcraft import xxxEnv

env = xxxEnv() 

total_steps = 5
total_variants = 250

for seed in range(total_variants):
    reset_info = env.reset(seed)
    task_images = reset_info[0]
    images, state, inventory, done, reward = reset_info[1]

    for _ in range(total_steps):
        actions = "your action here"
        images, state, inventory, done, reward = env.step(actions)

env.close()
```