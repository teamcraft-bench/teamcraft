async function killMob(bot, target, timeout = 300) {
    // return if timeout is not number
    if (typeof timeout !== "number") {
        throw new Error(`timeout for killMob must be a number`);
    }

    const weaponsForShooting = [
        "bow",
        "crossbow",
        "snowball",
        "ender_pearl",
        "egg",
        "splash_potion",
        "trident",
    ];
    const mainHandItem = bot.inventory.slots[bot.getEquipmentDestSlot("hand")];

    target = new Vec3(target.x+0.5, target.y, target.z+0.5)

    const entity = bot.nearestEntity(
        (entity) =>
            // entity.name === mobName &&
            entity.position.distanceTo(target) < 0.4
    );
    if (!entity) {
        bot.chat(`No entity near ${target}, please explore first`);
        _killMobFailCount++;
        if (_killMobFailCount > 10) {
            throw new Error(
                `killMob failed too many times, make sure you explore before calling killMob`
            );
        }
        return;
    }

    let droppedItem;
    if (mainHandItem && weaponsForShooting.includes(mainHandItem.name)) {
        bot.hawkEye.autoAttack(entity, mainHandItem.name);
        droppedItem = await waitForMobShot(bot, entity, timeout);
    } else {
        await bot.pvp.attack(entity);
        droppedItem = await waitForMobRemoved(bot, entity, timeout);
    }
    if (droppedItem) {
        await bot.collectBlock.collect(droppedItem, { ignoreNoPath: true });
    }
    // bot.save(`${mobName}_killed`);
}
