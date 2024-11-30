async function obtainBlock(bot, target) {
    // return if name is not string
    try{
        const targets = [];
        targets.push(bot.blockAt(target));
        const name = bot.blockAt(target).name;
        const blockByName = mcData.blocksByName[name];

        await bot.collectBlock.collect(targets, {
            ignoreNoPath: true,
            count: 1,
        });
        
        bot.save(`${name}_mined`);
    }catch (error) {
        console.log(error)
        throw error;
      }
}