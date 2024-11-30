async function takeOutFurnace(bot, target) {


    const furnaceBlock = bot.blockAt(target);

    if (!furnaceBlock) {
        throw new Error("No furnace nearby");
    } else {
        await bot.pathfinder.goto(
            new GoalLookAtBlock(furnaceBlock.position, bot.world)
        );
    }

    // Introduce a 15-second delay before executing the next lines
    await new Promise(resolve => setTimeout(resolve, 11000));

    const furnace = await bot.openFurnace(furnaceBlock);
    
    await furnace.takeOutput();

    bot1.emit("updateFurnace", furnaceBlock.position , furnace.inputItem(), furnace.fuelItem(), furnace.outputItem());
    bot2.emit("updateFurnace", furnaceBlock.position , furnace.inputItem(), furnace.fuelItem(), furnace.outputItem());
    await furnace.close();
}
