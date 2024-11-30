const { Observation } = require("./base");

class Furnaces extends Observation {
    constructor(bot) {
        super(bot);
        this.name = "nearbyFurnaces";
        this.furnaceItems = {};
        bot.on("updateFurnace", (position, inputSlot, fuelSlot, resultSlot) => {
            let contents = [];
            if (inputSlot) {
                contents.push(inputSlot.name);
            }
            if (fuelSlot) {
                contents.push(fuelSlot.name);
            }
            if (resultSlot) {
                contents.push(resultSlot.name);
            }
            this.furnaceItems[position] = contents;
        });
    }

    observe() {
        const furnaces = this.bot.findBlocks({
            matching: this.bot.registry.blocksByName.furnace.id,
            maxDistance: 32,
            count: 999,
        });
        furnaces.forEach((furnace) => {
            if (!this.furnaceItems.hasOwnProperty(furnace)) {
                this.furnaceItems[furnace] = "[]";
            }
        });
        return this.furnaceItems;
    }
}

module.exports = Furnaces;
