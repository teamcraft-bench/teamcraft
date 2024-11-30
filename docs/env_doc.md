# Benchmark Platform

TeamCraft provides task suite and benchmark for learning embodied Multi-Agent systems in Minecraft.

## Run

TeamCraft provides a Gym-style interface. Here is a very simple code snippet to instantiate the task "Build" and loop through all its 250 variants:

```python
from teamcraft import BreakEnv, BuildEnv, FarmEnv, SmeltEnv

env = BuildEnv() # can also be BreakEnv(), FarmEnv(), SmeltEnv()

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

BuildEnv, or BreakEnv, BuildEnv, FarmEnv, SmeltEnv takes following parameters:

- `--output_folder`: Folder path to save metadata JSON and logs (default: `./`)
- `--mc_port`: Minecraft server port (default: `2037`)
- `--mineflayer_port`: Mineflayer port (default: `3000`)

Save the above code as `temp.py`, and then run it with `xvfb-run`:

```bash
xvfb-run python temp.py
```

If you wish to use GPU in your code, an alternative to skip the `xvfb-run` (which is mutually exclusive with GPU) is to run [xserver.py](xserver.py) in a tmux shell:

```bash
# start tmux session
$ tmux new -s xserver 

# start X server on DISPLAY 0
# single X server should be sufficient for multiple instances of THOR
$ sudo python ./xserver.py 0  # if this throws errors e.g "(EE) Server terminated with error (1)" or "(EE) already running ..." try a display > 0

# detach from tmux shell
# Ctrl+b then d

# set DISPLAY variable to match X server
$ export DISPLAY=:0

python temp.py
```

## Observation and Action Space

For each step, TeamCraft's obversation includes RGB images for all working agents with a brid eye view of the playground, the block voxel information that's within playground and working agents' view distance, the inventory for each working agents, done, and reward.

```python
images, state, inventory, done, reward = env.step(actions)

images
>>> {"bot1": image(np.array(0, 255, shape=(3, 480, 640), dtype=np.uint8)),
     "bot2": image(np.array(0, 255, shape=(3, 480, 640), dtype=np.uint8)),
     ...
    }

inventory
>>> {"bot1": {item_name(str): count(int), item_name(str): count(int), ...},
     "bot2": {item_name(str): count(int), item_name(str): count(int), ...},
     ...
    }

state
>>> {
    "bot1": {
        "voxels": [
            [str, {"x": int, "y": int, "z": int}],  # Each voxel entry with a block type and coordinates
            ...
        ],
        "status": {
            "health": int,         # Health value (0-20)
            "food": int,           # Food level (0-20)
            "saturation": float,   # Saturation level (0+)
            "oxygen": int,         # Oxygen level (0-20)
            "position": {          # Current position of the bot
                "x": float,
                "y": float,
                "z": float
            },
            "velocity": {          # Current velocity of the bot
                "x": float,
                "y": float,
                "z": float
            },
            "yaw": float,          # Yaw rotation
            "pitch": float,        # Pitch rotation
            "onGround": bool,      # Whether bot is on the ground
            "equipment": [str or None, ...],  # List of equipped items
            "name": str,           # Bot's name
            "isInWater": bool,     # Whether bot is in water
            "isInLava": bool,      # Whether bot is in lava
            "isCollidedHorizontally": bool,  # Horizontal collision status
            "isCollidedVertically": bool,    # Vertical collision status
            "biome": str,          # Current biome name
            "entities": {str: float, ...},   # Nearby entities and distances
            "timeOfDay": str,      # Time of day (e.g., "day" or "night")
            "inventoryUsed": int,  # Count of used inventory slots
            "elapsedTime": int     # Elapsed time in seconds
        },
        "inventory": {str: int, ...},  # Inventory items with quantities
        "nearbyChests": {str: str, ...},  # Nearby chests with positions and contents
        "nearbyFurnaces": {str: str, ...},  # Nearby furnaces with positions and contents
        "onChat": None or str    # Chat message or None if no message
    },
    "bot2": { ... },             # Similar structure as "bot0"
    ...
}
```

*Note: for task involve 4 working agents, bot name starts from bot0 to bot3*

Each time the environment being reset, it will return the normal step info, along with task images.

```python
reset_info = env.reset(seed)

task_images = reset_info[0]
task_images
>>> {0: {"bot1": image(np.array(0, 255, shape=(3, 480, 640), dtype=np.uint8)),
         "bot2": image(np.array(0, 255, shape=(3, 480, 640), dtype=np.uint8)),
         ...
        },
     1: {"bot1": image(np.array(0, 255, shape=(3, 480, 640), dtype=np.uint8)),
         "bot2": image(np.array(0, 255, shape=(3, 480, 640), dtype=np.uint8)),
         ...
        },
     2: {"bot1": image(np.array(0, 255, shape=(3, 480, 640), dtype=np.uint8)),
         "bot2": image(np.array(0, 255, shape=(3, 480, 640), dtype=np.uint8)),
         ...
        }
    }
  

# Same structure as env.step()
images, state, inventory, done, reward = reset_info[1]
```

TeamCraft's action space are a list of string. The list should contains each working agent's action, up to one action per agents, and length of the list should be equal or smaller than total number of the working agents.

Inside each agents action string, it should be composed with action name, and action's coresponding parameters.

```python
actions
>>> [
    "ActionName(bot0, parameter_1, new Vec3(x,y,z))",
    "ActionName(bot1, parameter_1, parameter_2, new Vec3(x,y,z))",
    "ActionName(bot2, parameter_1)",
    ...
    ]
```

### Available Action Names


- **`placeItem(bot, name, new Vec3())`**:\
  Bot places a "name" item at given coordinates, upon verifying if the item is in inventory and the position is suitable. If necessary, it navigates to the position with retries for placement failures.

- **`mineBlock(bot, new Vec3())`**:\
Bot break a specified block at given coordinates. If specific conditions are met (e.g., block type persists), it enters a "force digger" mode to handle special blocks like cobwebs. 

- **`farm_work(bot, new Vec3(), work_type, name='')`**:\
  Directs the bot to perform farming tasks ("harvest" or "sow") around a specified position. In "harvest" mode, it locates and collects ripe crops, while in "sow" mode, it plants "name" seeds on prepared farmland. The function verifies the type of task and target position, using helper functions for block identification.

- **`obtainBlock(bot, new Vec3())`**:\
  Bot locates and collects a specified block at target coordinates, upon verifying if proper tools are equiped.

- **`putFuelFurnace(bot, fuelName, new Vec3())`**:\
  Bot places a "fuelName" fuel item into a furnace at given coordinates, upon verifying if the furnace's presence and fuel availability in inventory.

- **`putItemFurnace(bot, itemName, new Vec3())`**:\
  Bot places a "itemName" item into a furnace at given coordinates for smelting, verifying the item's availability in inventory and navigating to the furnace.

- **`takeOutFurnace(bot, new Vec3())`**:\
  Bot retrieves the output from a furnace at given coordinates. 

- **`killMob(bot, target, timeout = 300)`**:\
  Bot targets and kills a mob near specified coordinates, using a ranged or melee attack based on its equipped weapon. After successfully defeating the mob, it collects any dropped items. The function retries a limited number of times if no target is found within range, ensuring the area is explored before further attempts. 

## Available Methods

#### `env.reset(seed)`

Resets the environment to an initial state using the provided seed, will save metadata if previous run, and captures initial observations.

- **Parameters:**

  - `seed` (int): Seed value for environment initialization to ensure reproducibility.
- **Returns:**

  - `task_image` (dict): Initial observation images from different viewpoints.
  - `info` (tuple): Contains `image`, `state`, `inventory`, `done`, and `reward`.

#### `env.step(actions)`

Executes the given actions in the environment and updates the state.

- **Parameters:**

  - `actions` (str or None): Action commands for the agents. If `None`, no action is performed.
- **Returns:**

  - `image`: Rendered image after executing the actions.
  - `state`: Updated state of the environment.
  - `inventory`: Current inventory status of each agent.
  - `done` (bool): Indicates if the task is completed.
  - `reward` (float): Reward obtained after the action.

#### `env.close()`

Closes the environment, saves collected metadata to a JSON file, and performs cleanup operations.


## Available Variable in Env

TeamCraft provides a handful environment variable that might be helpful for the current task states.

- **`env.env`**: The main `teamCraft` environment instance.
- **`env.task_name`**: A string identifier for the current task.
- **`env.init_command`**: Initial command loaded from configuration files, used to set up the Minecraft world.
- **`env.bot_count`**: The total number of bots involved in the environment, initialized based on configuration data.
- **`env.done_input`**: Specifies the criteria or actions required for task completion.
- **`env.action_length`**: The length of the action list associated with the task, useful for tracking task progress.
- **`env.bot_list`**: List of bot names initialized from the configuration, used for controlling bots within tasks.
- **`env.center_position`**: Coordinates representing the center of the area of interest, used as a reference for bots’ focus.
- **`env.obs_command`**: List of commands issued to the bots to gather observations from the environment.
- **`env.time_step`**: Counter for the number of steps executed in the environment, incremented with each `step`.
- **`env.actions`**: Stores the latest actions executed in the environment.
- **`env.reward`**: A numerical value representing the bots' performance reward based on task-specific criteria.
- **`env.done`**: Boolean flag indicating whether the task is completed.
- **`env.task_image`**: Dictionary storing images related to each task step or observation, useful for visual progress tracking.
- **`env.observation`**: Contains the latest observation data returned from the environment.
- **`env.metadata`**: Dictionary storing detailed metadata for each time step, including action, reward, inventory, and bot states.
- **`env.inventory`**: Dictionary holding inventory data for each bot, extracted from the observations.
- **`env.total_placed`**: Counter for the total number of blocks placed by bots as part of the task.
- **`env.total_hit`**: Counter for the successful placements of blocks by bots within the defined area of interest.
- **`env.state`**: The current filtered voxel data representing the environment state within the area of interest.
- **`env.image`**: A rendered image of the environment, useful for visual debugging and inspection.

## Visualization

To see what agents doing in real time, login to the Minecraft server as an observer. 

To join our Minecraft, download and run Minecraft on your local machine:

- Purchase Minecraft game through [offical website](https://www.minecraft.net/en-us/store/minecraft-deluxe-collection-pc). Basic version is enough.
- Download Minecraft luncher from its [offical release](https://www.minecraft.net/en-us/download).
- Login to your Microsoft account on the luncher, and then choose Minecraft Java Edition. 
- Install required instance under "Installations" tab, click on "new installation", under "version", choose "release 1.16.4".
- Lunch instance you just installed, click on "multi-player".
- (Skip if you are running both your Minecraft instance and TeamCraft on the same machine). Forward your `mc_port` to you local machine. Use VS Code "[Port Forwarding](https://code.visualstudio.com/docs/editor/port-forwarding)" function to forward your MC Server port to the machine running Minecraft instance.
- Click on "Add server", use `localhost:{mc_port}` for the server address. Save and back to multi-player screen. You should see the server you just added.
- Join the server by double click on it. 
- To find your bots, you need OP privilege in the server. Run [op.py](../op.py) with `python op.py --username "YOUR_USER_NAME"` to add your account as OP. op.py takes following parameters:

  - `--username`: Minecraft username, case sensitive, required.
  - `--duration`: Duration (seconds)  to wait for user to join the server (default: 100)
  - `--mc_port`: Minecraft server port (default: `2037`)

- Use command `/gamemode spectator` to turn into spectator mode, and then use `/tp bot1` to find your bots. You can input command by hitting `T` key on your keyboard, and a input bar will show up at the bottom.
- To view first-person view of your bot, get close to the bot you wish to view, left click on the bot while you looking directly at the bot and close to bot. You view will be attached to that bot. Hit `Shift` to exit.

## System Requirement For Data Generation

To run data generation, the minimum system requirements are:

- **CPU**: 8 cores (or 16 threads) @3 GHz or higher
- **Memory**: 16 GB RAM
- **Disk Space**: 20 GB available
- **GPU**: Not required

Tested configuration on AWS EC2:

- **OS Image**: Ubuntu Server 22.04 LTS (HVM), EBS General Purpose (SSD)
- **Instance Type**: c6a.4xlarge
- **Storage**: 100 GiB gp2

[*Note: system requirements could be much lower if choose to run under voxel only mode (no RGB rendering).*]
