async function getItemFromChest(bot, chestPosition, itemsToGet) {
    // return if chestPosition is not Vec3
    if (!(chestPosition instanceof Vec3)) {
        bot.chat("chestPosition for getItemFromChest must be a Vec3");
        return;
    }
    await moveToChest(bot, chestPosition);
    const chestBlock = bot.blockAt(chestPosition);
    const chest = await bot.openContainer(chestBlock);
    for (const name in itemsToGet) {
        const itemByName = mcData.itemsByName[name];
        if (!itemByName) {
            bot.chat(`No item named ${name}`);
            continue;
        }

        const item = chest.findContainerItem(itemByName.id);
        if (!item) {
            bot.chat(`I don't see ${name} in this chest`);
            continue;
        }
        try {
            await chest.withdraw(item.type, null, itemsToGet[name]);
        } catch (err) {
            bot.chat(`Not enough ${name} in chest.`);
        }
    }
    await closeChest(bot, chestBlock);
}

async function depositItemIntoChest(bot, chestPosition, itemsToDeposit) {
    // return if chestPosition is not Vec3
    if (!(chestPosition instanceof Vec3)) {
        throw new Error(
            "chestPosition for depositItemIntoChest must be a Vec3"
        );
    }
    // await moveToChest(bot, chestPosition);
    const chestBlock = bot.blockAt(chestPosition);
    const chest = await bot.openContainer(chestBlock);
    
    const itemFromName = mcData.itemsByName[itemsToDeposit];
    if (!itemFromName) {
        bot.chat(`No item named ${itemsToDeposit}`);
    }
    // const item = bot.inventory.findInventoryItem(itemByName.id);
    const inventory = bot.currentWindow || bot.inventory;
    const item = itemByName(inventory.items(), itemsToDeposit);

    if (!item) {
        bot.chat(`No ${itemsToDeposit} in inventory`);
    }
    try {
        
        await chest.deposit(item.type, null, 1);
    } catch (err) {
        bot.chat(`Not enough ${itemsToDeposit} in inventory.`);
    }
    
    bot1.emit("closeChest", {itemsToDeposit}, chestBlock.position);
    bot2.emit("closeChest", {itemsToDeposit}, chestBlock.position);
    
    await closeChest(bot, chestBlock);
}

async function checkItemInsideChest(bot, chestPosition) {
    // return if chestPosition is not Vec3
    if (!(chestPosition instanceof Vec3)) {
        throw new Error(
            "chestPosition for depositItemIntoChest must be a Vec3"
        );
    }
    await moveToChest(bot, chestPosition);
    const chestBlock = bot.blockAt(chestPosition);
    await bot.openContainer(chestBlock);
    await closeChest(bot, chestBlock);
}

async function moveToChest(bot, chestPosition) {
    if (!(chestPosition instanceof Vec3)) {
        throw new Error(
            "chestPosition for depositItemIntoChest must be a Vec3"
        );
    }
    if (chestPosition.distanceTo(bot.entity.position) > 32) {
        bot.chat(
            `/tp ${chestPosition.x} ${chestPosition.y} ${chestPosition.z}`
        );
        await bot.waitForTicks(20);
    }
    const chestBlock = bot.blockAt(chestPosition);
    if (chestBlock.name !== "chest") {
        bot1.emit("removeChest", chestPosition);
        bot2.emit("removeChest", chestPosition);
        throw new Error(
            `No chest at ${chestPosition}, it is ${chestBlock.name}`
        );
    }
    await bot.pathfinder.goto(
        new GoalLookAtBlock(chestBlock.position, bot.world, {})
    );
    return chestBlock;
}

async function listItemsInChest(bot, chestBlock) {
    const chest = await bot.openContainer(chestBlock);
    const items = chest.containerItems();
    if (items.length > 0) {
        const itemNames = items.reduce((acc, obj) => {
            if (acc[obj.name]) {
                acc[obj.name] += obj.count;
            } else {
                acc[obj.name] = obj.count;
            }
            return acc;
        }, {});
        bot1.emit("closeChest", itemNames, chestBlock.position);
        bot2.emit("closeChest", itemNames, chestBlock.position);
    } else {
        bot1.emit("closeChest", {}, chestBlock.position);
        bot2.emit("closeChest", {}, chestBlock.position);
    }
    
    return chest;
}

async function updatePlayerChestInventory(bot, chestx, chesty, chestz){
   
    let chestPosition = new Vec3(chestx, chesty, chestz);
    const chestBlock = bot.blockAt(chestPosition);
    bot.chat('/data modify block -217 32 -51 Items set from entity nikepupu9 Inventory');
    const chest = await bot.openContainer(chestBlock);
    const items = chest.containerItems();
    await bot.waitForTicks(40);

    if (items.length > 0) {
        const itemNames = items.reduce((acc, obj) => {
            if (acc[obj.name]) {
                acc[obj.name] += obj.count;
            } else {
                acc[obj.name] = obj.count;
            }
            return acc;
        }, {});
        bot.emit("closeChest", itemNames, chestBlock.position);
    } else {
        bot.emit("closeChest", {}, chestBlock.position);
    }

    await chest.close();
    
}

async function closeChest(bot, chestBlock) {
    try {
        const chest = await listItemsInChest(bot, chestBlock);
        await chest.close();
    } catch (err) {
        await bot.closeWindow(chestBlock);
    }
}

function itemByName(items, name) {
    for (let i = 0; i < items.length; ++i) {
        const item = items[i];
        if (item && item.name === name) return item;
    }
    return null;
}
