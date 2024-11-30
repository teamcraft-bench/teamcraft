// Blocks = require("./blocks")
const { Observation } = require("./base");

class Voxels extends Observation {
    constructor(bot) {
        super(bot);
        this.name = "voxels";
    }

    observe() {
        return Array.from(getSurroundingBlocks(this.bot, 32, 4, 32));
    }
}

class BlockRecords extends Observation {
    constructor(bot) {
        super(bot);
        this.name = "blockRecords";
        this.records = new Set();
        this.tick = 0;
        bot.on("physicsTick", () => {
            this.tick++;
            if (this.tick >= 100) {
                const items = getInventoryItems(this.bot);
                getSurroundingBlocks(this.bot, 32, 4, 32).forEach((block) => {
                    if (!items.has(block)) {
                        if (typeof block === 'string') {
                            this.records.add(block);
                        }
                        else{
                            this.records.add(block[0]);
                        }
                    }
                });
                this.tick = 0;
            }
        });
    }

    observe() {
        return Array.from(this.records);
    }

    reset() {
        this.records = new Set();
    }
}

function getSurroundingBlocks(bot, x_distance, y_distance, z_distance) {
    const surroundingBlocks = new Set();

    for (let x = -x_distance; x <= x_distance; x++) {
        for (let y = -y_distance; y <= y_distance; y++) {
            for (let z = -z_distance; z <= z_distance; z++) {
                const block = bot.blockAt(bot.entity.position.offset(x, y, z));
                if (block && block.type !== 0) {
                    if (['water','cyan_concrete', 'oak_wood', 'hay_block', 'glass', 'pink_wool', 'obsidian','smooth_quartz', 'gold_ore', 'sponge', 'sea_lantern','beetroots','farmland','wheat','potatoes','carrots','oak_log', 'gold_ore', 'acacia_log', 'chest', 'furnace', 'bookshelf', 'crafting_table', 'oak_fence', 'acacia_fence', 'birch_log', 'coal_ore', 'bricks', 'sandstone', 'stone', 'iron_ore', 'anvil', 'dirt', 'sand', 'grass_block', 'clay', 'cobweb', 'oak_planks', 'emerald_block', 'bricks', 'pumpkin', 'orange_concrete', 'purple_wool', 'end_stone', 'furnace', 'oak_log', 'chest', 'gold_ore', 'iron_ore', 'sand', 'red_sand', 'sandstone', 'cobblestone', 'coal_ore', 'oak_log', 'birch_log', 'acacia_log', 'spruce_log', 'oak_planks', 'birch_planks' , 'acacia_planks', 'spruce_planks', 'clay'].includes(block.name)) { 
                        if (['beetroots','wheat','potatoes','carrots', 'farmland'].includes(block.name)) {
                            surroundingBlocks.add([block.name, bot.entity.position.offset(x, y, z), block.metadata]);
                        }
                        else{
                            let dist = Math.sqrt(x * x + y * y + z * z);
                            // surroundingBlocks.add([block.name, dist]);
                            surroundingBlocks.add([block.name, bot.entity.position.offset(x, y, z)]);
                        }
                    }
                    else{
                        
                        surroundingBlocks.add(block.name);
                    
                    }
                }
            }
        }
    }
    // console.log(surroundingBlocks);
    return surroundingBlocks;
}

function getInventoryItems(bot) {
    const items = new Set();
    bot.inventory.items().forEach((item) => {
        if (item) items.add(item.name);
    });
    return items;
}

module.exports = { Voxels, BlockRecords };
