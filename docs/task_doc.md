# Task Break

https://github.com/user-attachments/assets/4fe3b0f2-2615-406c-8195-fea8aaa41df3

Task break challenges agents to remove all blocks from a specified $6\times6$ area. Agents must employ appropriate tools to break the blocks, which vary in durability, thereby requiring multiple interactions for complete removal. The use of correct tools can dramatically reduce the time required to remove blocks (up to $3\times$ speedup). The agents must manage their tool assignments to optimize block-breaking efficiency such that the time steps needed for one task can be minimized. Strategic coordination is essential in this task as agents need to dynamically decide which blocks to target based on their current tools and help each other minimize the overall time taken to clear the area.

Evaluation config file for breaking task is specify as below:

| Config/Variant Seed     |                               Description           |
| ----------------------- | :-------------------------------------------------: |
| 0   - 49                |  Same distribution shape as training data (Average) |
| 50  - 99                |  New target placement shape                         |
| 100 - 149               |  New target material                                |
| 150 - 199               |  New scene                                          |
| 200 - 249               |  4 agents                                           |

# Task Build

https://github.com/user-attachments/assets/c919acaa-97c5-40f3-a541-67328ffb7de3

Task build requires agents to collaboratively erect a structure based on a provided three orthographic views blueprint (front, side, and top). Each agent possesses a unique inventory of building blocks necessary for the construction. The task requires agents not only to understand their individual capabilities and inventories, but also to plan their movements and actions in coordination with other agents so as to efficiently construct the building on a designated $5\times5$ foundation.

Evaluation config file for building task is specify as below:

| Config/Variant Seed     |                               Description           |
| ----------------------- | :-------------------------------------------------: |
| 0   - 49                |  Same distribution shape as training data (Average) |
| 50  - 99                |  New target placement shape                         |
| 100 - 149               |  New target material                                |
| 150 - 199               |  New scene                                          |
| 200 - 249               |  4 agents                                           |


# Task Farm

https://github.com/user-attachments/assets/9e6d8fd7-491c-46fd-86fa-3f5624102a79

Task farm is designed to simulate agricultural activities, where agents must sow and harvest crops. Agents are required to plant seeds on designated farmland plots and observe plantings until the crops reach maturity. Each crop has several growth stages from Level~0 (newly planted) to Level~7 (fully grown), and agents must identify when crops are ready to be harvested. The challenge lies in dynamically allocating tasks among agents based on their positions, available seeds, and the maturity of different crops. Effective task distribution and coordinated actions ensure maximum yield and efficiency. For example, some agents can sow while others are planting, and they should stop when their total crop yield is satisfactory.


Evaluation config file for farming task is specify as below:

| Config/Variant Seed     |                               Description           |
| ----------------------- | :-------------------------------------------------: |
| 0   - 49                |  Same distribution shape as training data (Average) |
| 100 - 149               |  New target corps                                   |
| 150 - 199               |  New scene                                          |
| 200 - 249               |  4 agents                                           |


# Task Smelt


https://github.com/user-attachments/assets/552aecf6-07a1-4c62-8f9c-7cafab54420c


Task smelt requires agents to obtain items processed using furnaces by gathering materials and coordinating actions. Agents collect resources from the environment---by harvesting blocks or killing mobs---and place them, or existing inventory items, into furnaces as smelting inputs. The output will be the final goal item that can be categorized as food or item, where food can be ``cooked beef``, ``cooked porkchop``, or ``baked potato``, and item can be ``glass`` or ``gold ingot`` by smelting sand or gold ore, respectively. Agents must also gather fuel (e.g., coal or lava buckets), with each furnace accepting only one type of fuel. Furnaces are placed near the playground center (one or two per task) and automatically smelt when supplied with fuel and items. Agents must use the provided tools, communicate effectively, and assign tasks efficiently due to dependencies in the smelting process.

Evaluation config file for smelting task is specify as below:

| Config/Variant Seed     |                               Description           |
| ----------------------- | :-------------------------------------------------: |
| 0   - 49                |  Same distribution shape as training data (Average) |
| 50  - 99                |  New furnace count                                  |
| 100 - 149               |  New goal item type                                 |
| 150 - 199               |  New scene                                          |
| 200 - 249               |  4 agents                                           |

