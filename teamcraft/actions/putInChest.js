async function putInChest(bot, itemName) {
    if (typeof itemName !== "string" ) {
        throw new Error("itemName must be a string");
    }
    const chestBlock = bot.findBlock({
        matching: mcData.blocksByName.chest.id,
        maxDistance: 8,
    });
    if (!chestBlock) {
        throw new Error("No chest nearby");
    } 
   
    await depositItemIntoChest(bot, chestBlock.position, itemName );
}
