async function goto(bot, locationName) {
    const blockByName = mcData.blocksByName[locationName];
    let block; // Define block here so it's in the outer scope.
    let is_entity = false;
    if (['furnace', 'oak_log', 'chest', 'gold_ore', 'iron_ore', 'sand', 'red_sand', 'sandstone', 'cobblestone', 'coal_ore', 'oak_log', 'birch_log', 'acacia_log', 'spruce_log', 'oak_planks', 'birch_planks' , 'acacia_planks', 'spruce_planks'].includes(locationName)) {
        block = bot.findBlock({
            matching: blockByName.id,
            maxDistance: 48,
        });
        
    } else if (['cow', 'mooshroom', 'rabbit', 'sheep', 'chicken', 'pig'].includes(locationName)) {
        block = bot.nearestEntity(
            (entity) =>
                entity.name === locationName && // Change mobName to locationName
                entity.position.distanceTo(bot.entity.position) < 48
        );
        is_entity = true;
    }
    
    if (!block) {
        throw new Error("No " + locationName + " nearby");
    } else {
        if(!is_entity){
            await bot.pathfinder.goto(
                // new GoalLookAtBlock(block.position, bot.world)
                new GoalGetToBlock(block.position.x, block.position.y, block.position.z)
            );
        } else {
            await bot.pathfinder.goto(
                new GoalFollow(block, 1)
            );
        }
    }
}