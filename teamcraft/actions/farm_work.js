/**
 * Conducts specified farming tasks ("harvest" or "sow") at a specific position.
 * This asynchronous function directs a bot to either harvest ripe crops or sow seeds based on the `work_type` parameter.
 * It leverages helper functions `blockToSow` and `blockToHarvest` to identify suitable blocks for the given tasks,
 * and performs the necessary actions if applicable blocks are found.
 *
 * @param {Object} bot - The bot instance executing the tasks.
 * @param {Vec3} target_position - The target position around which the bot will perform farming tasks.
 * @param {string} work_type - Specifies the farming action: "harvest" for harvesting ripe crops or "sow" for planting seeds.
 *
 * @throws {Error} If `target_position` is not a Vec3 instance or `work_type` is not a string.
 * @throws {Error} If no suitable blocks are found, prompting the need for the bot to move or perform other actions.
 *
 *
 * Example:
 *   farm_work(botInstance, new Vec3(10, 64, 10), "sow"); // Commands the bot to sow seeds around the position (10, 64, 10).
 */



async function farm_work(bot, target_position, work_type, name='') {

    await bot.chat(`Starting to ${work_type} at ${target_position.x}, ${target_position.y}, ${target_position.z}`)
    function blockToSow(target_position) {
        const target_block = bot.blockAt(target_position)
        if (target_block.type === bot.registry.blocksByName.farmland.id && 
            (!bot.blockAt(target_block.position.offset(0, 1, 0)) || bot.blockAt(target_block.position.offset(0, 1, 0)).type === 0)){
            return target_block
        }
        else{
            return null}
    }

    function blockToHarvest(target_position) {
        const target_block = bot.blockAt(target_position)
        if (target_block && target_block.name === 'beetroots'){
            if (target_block.metadata === 3){
                return target_block
            }
            else{
                return null
            }
        }
        if (target_block && target_block.metadata === 7) {
            return target_block
        }
        else{
            return null}
    }

    if (typeof target_position !== typeof bot.entity.position) {
        throw new Error(`target_position must be a position`);
    }
    if (typeof work_type !== "string") {
        throw new Error(`work_type for farm_work must be a string`);
    }

    try {
        // Do harvest work
        if (work_type === "harvest") {
            const toHarvest = blockToHarvest(target_position);
            if (!toHarvest) {
                bot.chat(`No crops nearby, please explore first`);
                throw new Error(`No crops nearby, please explore first`)
            }
            let movements = new Movements(bot)
            movements.canDig = false;
            movements.allow1by1towers = false;
            movements.placeCost = 999;
            bot.pathfinder.setMovements(movements)
            await bot.chat(`Harvesting at ${toHarvest.position.x}, ${toHarvest.position.y}, ${toHarvest.position.z}`)
            const p = toHarvest.position.offset(0, -1, 0)
            const goal = new GoalLookAtBlock(p, bot.world)
            await bot.pathfinder.goto(goal)
            await bot.lookAt(toHarvest.position)
            const droppedItemPromise = waitForItemDrop(bot, 3000);
            await bot.dig(toHarvest)
            const droppedItemPromise1 = waitForItemDrop(bot, 3000);
            const droppedItem = await droppedItemPromise;
            await bot.collectBlock.collect(droppedItem);
            const droppedItem1 = await droppedItemPromise1;
            await bot.collectBlock.collect(droppedItem1);
            await bot.lookAt(toHarvest.position)

        }
        if (work_type === "sow") {
            const toSow = blockToSow(target_position);
            if (!toSow) {
                bot.chat(`No empty farm land nearby, please explore first`);
                throw new Error(`No empty farm land nearby, please explore first`);
            }
            bot.pathfinder.setMovements(new Movements(bot))
            const goal = new GoalLookAtBlock(toSow.position, bot.world)
            await bot.pathfinder.goto(goal)
            await bot.equip(bot.registry.itemsByName[name].id, 'hand')
            await bot.placeBlock(toSow, new Vec3(0, 1, 0))
            await bot.lookAt(toSow.position)
        }
    } catch (e) {
        bot.chat(`Error: ${e.message}`)
        console.log(e)
        throw e
    }
    bot.save(`${work_type}_done`);
}


function waitForItemDrop(bot, timeout = 300) {
    return new Promise((resolve, reject) => {
        let droppedItem = null;
        const timeoutId = setTimeout(() => {
            reject(new Error(`Failed to find item.`));
        }, timeout);

        function onItemDrop(item) {
            if (bot.entity.position.distanceTo(item.position) <= 8) {
                droppedItem = item;
            }
            else{
                bot.chat(`Item dropped too far away`)
            }
            clearTimeout(timeoutId);
            bot.removeListener("itemDrop", onItemDrop);
            resolve(droppedItem);
        }

        bot.on("itemDrop", onItemDrop);
    });
}