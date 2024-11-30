async function mineBlock(bot, target) {
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

        const blocks_new = [];
        const block_type = bot.blockAt(target).type;
        if (block_type !== 0){
            blocks_new.push(target);
            
        }
        if (blocks_new.length !== 0) {
            bot.chat("enter the force digger stage");
            for (let i = 0; i < blocks_new.length; i++) {
                let movements = new Movements(bot)
                movements.canDig = false;
                movements.allow1by1towers = false;
                movements.placeCost = 999;
                bot.pathfinder.setMovements(movements)
                bot.chat(`current block ${blocks_new[i]}`)
                if (name === "cobweb"){
                    blocks_new[i] = blocks_new[i].offset(0, -1, 0)}
                const goal = new GoalLookAtBlock(blocks_new[i], bot.world)
                await bot.pathfinder.goto(goal)
                if (name === "cobweb"){
                    blocks_new[i] = blocks_new[i].offset(0, 1, 0)}
                await bot.dig(bot.blockAt(blocks_new[i]), "raycast")
            }
        }
        bot.save(`${name}_mined`);
    }catch (error) {
        console.log(error)
        throw error;
      }
}
