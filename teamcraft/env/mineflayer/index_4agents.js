const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");
const mineflayer = require("mineflayer");

const screenshotTaker = require('prismarine-viewer').render

const skills = require("./lib/skillLoader");
const { initCounter, getNextTime } = require("./lib/utils");
const obs = require("./lib/observation/base");
const OnChat = require("./lib/observation/onChat");
const OnError = require("./lib/observation/onError");
const { Voxels, BlockRecords } = require("./lib/observation/voxels");
const Status = require("./lib/observation/status");
const Inventory = require("./lib/observation/inventory");
const OnSave = require("./lib/observation/onSave");
const Chests = require("./lib/observation/chests");
const Furnaces = require("./lib/observation/furnaces");
const { plugin: tool } = require("mineflayer-tool");

let bot0 = null;
let bot1 = null;
let bot2 = null;
let bot3 = null;
let bot4 = null;
const app = express();

let bot0_viewer = null;
let bot1_viewer = null;
let bot2_viewer = null;
let bot3_viewer = null;
let bot4_viewer = null;

app.use(bodyParser.json({ limit: "50mb" }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: false }));

app.post("/start", (req, res) => {
    if (bot0) onDisconnect("Restarting bot0");
    if (bot1) onDisconnect("Restarting bot1");
    if (bot2) onDisconnect("Restarting bot2");
    if (bot3) onDisconnect("Restarting bot3");
    if (bot4) onDisconnect("Restarting bot4");
    bot0 = null;
    bot1 = null;
    bot2 = null;
    bot3 = null;
    bot4 = null;
    console.log(req.body);
    const ip = "localhost"

    bot0 = mineflayer.createBot({
        host: ip, // minecraft server ip
        port: req.body.port, // minecraft server port
        username: "bot0", // minecraft username
        disableChatSigning: true,
        checkTimeoutInterval: 60 * 60 * 1000,
    });

    bot1 = mineflayer.createBot({
        host: ip, // minecraft server ip
        port: req.body.port, // minecraft server port
        username: "bot1", // minecraft username
        disableChatSigning: true,
        checkTimeoutInterval: 60 * 60 * 1000,
    });

    bot2 = mineflayer.createBot({
        host: ip, // minecraft server ip
        port: req.body.port, // minecraft server port
        username: "bot2", // minecraft username
        disableChatSigning: true,
        checkTimeoutInterval: 60 * 60 * 1000,
    });

    bot3 = mineflayer.createBot({
        host: ip, // minecraft server ip
        port: req.body.port, // minecraft server port
        username: "bot3", // minecraft username
        disableChatSigning: true,
        checkTimeoutInterval: 60 * 60 * 1000,
    });
    bot4 = mineflayer.createBot({
        host: ip, // minecraft server ip
        port: req.body.port, // minecraft server port
        username: "bot4", // minecraft username
        disableChatSigning: true,
        checkTimeoutInterval: 60 * 60 * 1000,
    });

    
    bot0.once("error", onConnectionFailed);
    bot1.once("error", onConnectionFailed);
    bot2.once("error", onConnectionFailed);
    bot3.once("error", onConnectionFailed);
    bot4.once("error", onConnectionFailed);

    // Event subscriptions
    bot0.waitTicks = req.body.waitTicks;
    bot0.globalTickCounter = 0;
    bot0.stuckTickCounter = 0;
    bot0.stuckPosList = [];
    bot0.iron_pickaxe = false;
    bot0.on("kicked", onDisconnect);

    bot1.waitTicks = req.body.waitTicks;
    bot1.globalTickCounter = 0;
    bot1.stuckTickCounter = 0;
    bot1.stuckPosList = [];
    bot1.iron_pickaxe = false;
    bot1.on("kicked", onDisconnect);

    bot2.waitTicks = req.body.waitTicks;
    bot2.globalTickCounter = 0;
    bot2.stuckTickCounter = 0;
    bot2.stuckPosList = [];
    bot2.iron_pickaxe = false;
    bot2.on("kicked", onDisconnect);

    bot3.waitTicks = req.body.waitTicks;
    bot3.globalTickCounter = 0;
    bot3.stuckTickCounter = 0;
    bot3.stuckPosList = [];
    bot3.iron_pickaxe = false;
    bot3.on("kicked", onDisconnect);

    bot4.waitTicks = req.body.waitTicks;
    bot4.globalTickCounter = 0;
    bot4.stuckTickCounter = 0;
    bot4.stuckPosList = [];
    bot4.iron_pickaxe = false;
    bot4.on("kicked", onDisconnect);

    // mounting will cause physicsTick to stop
    bot0.on("mount", () => {
        bot0.dismount();
    });

    bot1.on("mount", () => {
        bot1.dismount();
    });

    bot2.on("mount", () => {
        bot2.dismount();
    });

    bot3.on("mount", () => {
        bot3.dismount();
    });

    bot4.on("mount", () => {
        bot4.dismount();
    });

    bot4.on('chat', async (username, message) => {
        const args = message.split(' ')
        if (args[0] === 'startRecoding') {
            bot0_viewer = screenshotTaker(bot0, {width: 640, height: 480}) 
            bot1_viewer = screenshotTaker(bot1, {width: 640, height: 480}) 
            bot2_viewer = screenshotTaker(bot2, {width: 640, height: 480}) 
            bot3_viewer = screenshotTaker(bot3, {width: 640, height: 480}) 
            bot4_viewer = screenshotTaker(bot4, {width: 640, height: 480}) 
            bot4.chat("start recording")
        }
    })
    
    console.log('mineflyer index file init...')

    bot1.once("spawn", async () => {
        bot1.removeListener("error", onConnectionFailed);
        let itemTicks = 1;
        
        bot0.chat("/clear @s");
        bot1.chat("/clear @s");
        bot2.chat("/clear @s");
        bot3.chat("/clear @s");
        bot4.chat("/clear @s");
        await bot1.waitForTicks(bot1.waitTicks * 3);
        

        bot1.chat('/time set day');
        bot1.chat('/gamerule doDaylightCycle false');
        bot1.chat('/weather clear');
        bot1.chat('/gamerule doWeatherCycle false');

        // bot0_viewer = screenshotTaker(bot0, {width: 640, height: 480}) 
        // bot1_viewer = screenshotTaker(bot1, {width: 640, height: 480}) 
        // bot2_viewer = screenshotTaker(bot2, {width: 640, height: 480}) 
        // bot3_viewer = screenshotTaker(bot3, {width: 640, height: 480}) 
        // bot4_viewer = screenshotTaker(bot4, {width: 640, height: 480}) 

 
        const { pathfinder } = require("mineflayer-pathfinder");
        const tool = require("mineflayer-tool").plugin;
        const collectBlock = require("mineflayer-collectblock").plugin;
        const pvp = require("mineflayer-pvp").plugin;
        const minecraftHawkEye = require("minecrafthawkeye");

        bot0.loadPlugin(pathfinder);
        bot0.loadPlugin(tool);
        bot0.loadPlugin(collectBlock);
        bot0.loadPlugin(pvp);
        bot0.loadPlugin(minecraftHawkEye);
        obs.inject(bot0, [
            OnChat,
            OnError,
            Voxels,
            Status,
            Inventory,
            OnSave,
            Chests,
            BlockRecords,
            Furnaces,
        ]);
        skills.inject(bot0);
        if (req.body.spread) {
            bot0.chat(`/spreadplayers ~ ~ 0 300 under 80 false @s`);
            await bot0.waitForTicks(bot0.waitTicks);
        }
        initCounter(bot0);


        bot1.loadPlugin(pathfinder);
        bot1.loadPlugin(tool);
        bot1.loadPlugin(collectBlock);
        bot1.loadPlugin(pvp);
        bot1.loadPlugin(minecraftHawkEye);

        obs.inject(bot1, [
            OnChat,
            OnError,
            Voxels,
            Status,
            Inventory,
            OnSave,
            Chests,
            BlockRecords,
            Furnaces,
        ]);
        skills.inject(bot1);

        if (req.body.spread) {
            bot1.chat(`/spreadplayers ~ ~ 0 300 under 80 false @s`);
            await bot1.waitForTicks(bot1.waitTicks);
        }
        initCounter(bot1);


        bot2.loadPlugin(pathfinder);
        bot2.loadPlugin(tool);
        bot2.loadPlugin(collectBlock);
        bot2.loadPlugin(pvp);
        bot2.loadPlugin(minecraftHawkEye);

        obs.inject(bot2, [
            OnChat,
            OnError,
            Voxels,
            Status,
            Inventory,
            OnSave,
            Chests,
            BlockRecords,
            Furnaces,
        ]);
        skills.inject(bot2);

        if (req.body.spread) {
            bot2.chat(`/spreadplayers ~ ~ 0 300 under 80 false @s`);
            await bot2.waitForTicks(bot2.waitTicks);
        }

        initCounter(bot2);


        bot3.loadPlugin(pathfinder);
        bot3.loadPlugin(tool);
        bot3.loadPlugin(collectBlock);
        bot3.loadPlugin(pvp);
        bot3.loadPlugin(minecraftHawkEye);
        obs.inject(bot3, [
            OnChat,
            OnError,
            Voxels,
            Status,
            Inventory,
            OnSave,
            Chests,
            BlockRecords,
            Furnaces,
        ]);
        skills.inject(bot3);
        if (req.body.spread) {
            bot3.chat(`/spreadplayers ~ ~ 0 300 under 80 false @s`);
            await bot3.waitForTicks(bot3.waitTicks);
        }
        
        initCounter(bot3);


        bot4.loadPlugin(pathfinder);
        bot4.loadPlugin(tool);
        bot4.loadPlugin(collectBlock);
        bot4.loadPlugin(pvp);
        bot4.loadPlugin(minecraftHawkEye);
        obs.inject(bot4, [
            OnChat,
            OnError,
            Voxels,
            Status,
            Inventory,
            OnSave,
            Chests,
            BlockRecords,
            Furnaces,
        ]);
        skills.inject(bot4);
        if (req.body.spread) {
            bot4.chat(`/spreadplayers ~ ~ 0 300 under 80 false @s`);
            await bot4.waitForTicks(bot4.waitTicks);
        }
        initCounter(bot4);


        await bot4.waitForTicks(bot4.waitTicks * itemTicks);
        await bot3.waitForTicks(bot3.waitTicks * itemTicks);
        await bot2.waitForTicks(bot2.waitTicks * itemTicks);
        await bot1.waitForTicks(bot1.waitTicks * itemTicks);
        await bot0.waitForTicks(bot1.waitTicks * itemTicks);

        res.json({bot0: bot0.observe(), bot1: bot1.observe(), bot2: bot2.observe(), bot3: bot3.observe(), bot4: bot4.observe()});
    });

    function onConnectionFailed(e) {
        console.log(e);
        bot0 = null;
        bot1 = null;
        bot2 = null;
        bot3 = null;
        bot4 = null;
        res.status(400).json({ error: e });
    }
    function onDisconnect(message) {

        if (bot0.viewer) {
            bot0.viewer.close();
        }
        bot0.end();
        console.log(message);
        bot0 = null;

        if (bot1.viewer) {
            bot1.viewer.close();
        }
        bot1.end();
        console.log(message);
        bot1 = null;

        if (bot2.viewer) {
            bot2.viewer.close();
        }
        bot2.end();
        console.log(message);
        bot2 = null;

        if (bot3.viewer) {
            bot3.viewer.close();
        }
        bot3.end();
        console.log(message);
        bot3 = null;
        
        if (bot4.viewer) {
            bot4.viewer.close();
        }
        bot4.end();
        console.log(message);
        bot4 = null;
    }
});

app.post("/step", async (req, res) => {
    // import useful package
    let response_sent = false;
    function otherError(err) {
        console.log("Uncaught Error");
        bot1.emit("error", handleError(err));
        bot1.waitForTicks(bot1.waitTicks).then(() => {
            if (!response_sent) {
                response_sent = true;
                res.json({bot0: bot0.observe(), bot1: bot1.observe(), bot2: bot2.observe(), bot3: bot3.observe(), bot4: bot4.observe()});
            }
        });
    }

    process.on("uncaughtException", otherError);

    const mcData = require("minecraft-data")(bot1.version);
    mcData.itemsByName["leather_cap"] = mcData.itemsByName["leather_helmet"];
    mcData.itemsByName["leather_tunic"] =
        mcData.itemsByName["leather_chestplate"];
    mcData.itemsByName["leather_pants"] =
        mcData.itemsByName["leather_leggings"];
    mcData.itemsByName["leather_boots"] = mcData.itemsByName["leather_boots"];
    mcData.itemsByName["lapis_lazuli_ore"] = mcData.itemsByName["lapis_ore"];
    mcData.blocksByName["lapis_lazuli_ore"] = mcData.blocksByName["lapis_ore"];
    const {
        Movements,
        goals: {
            Goal,
            GoalBlock,
            GoalNear,
            GoalXZ,
            GoalNearXZ,
            GoalY,
            GoalGetToBlock,
            GoalLookAtBlock,
            GoalBreakBlock,
            GoalCompositeAny,
            GoalCompositeAll,
            GoalInvert,
            GoalFollow,
            GoalPlaceBlock,
        },
        pathfinder,
        Move,
        ComputedPath,
        PartiallyComputedPath,
        XZCoordinates,
        XYZCoordinates,
        SafeBlock,
        GoalPlaceBlockOptions,
    } = require("mineflayer-pathfinder");
    const { Vec3 } = require("vec3");

    // Set up pathfinder
    const movements0 = new Movements(bot0, mcData);
    movements0.canDig = false;
    movements0.allow1by1towers = false;
    movements0.placeCost = 999;
    bot0.pathfinder.setMovements(movements0);

    bot0.globalTickCounter = 0;
    bot0.stuckTickCounter = 0;
    bot0.stuckPosList = [];

    const movements = new Movements(bot1, mcData);
    movements.canDig = false;
    movements.allow1by1towers = false;
    movements.placeCost = 999;
    bot1.pathfinder.setMovements(movements);

    bot1.globalTickCounter = 0;
    bot1.stuckTickCounter = 0;
    bot1.stuckPosList = [];

    const movements2 = new Movements(bot2, mcData);
    movements2.canDig = false;
    movements2.allow1by1towers = false;
    movements2.placeCost = 999;
    bot2.pathfinder.setMovements(movements2);

    bot2.globalTickCounter = 0;
    bot2.stuckTickCounter = 0;
    bot2.stuckPosList = [];

    const movements3 = new Movements(bot3, mcData);
    movements3.canDig = false;
    movements3.allow1by1towers = false;
    movements3.placeCost = 999;
    bot3.pathfinder.setMovements(movements3);

    bot3.globalTickCounter = 0;
    bot3.stuckTickCounter = 0;
    bot3.stuckPosList = [];

    const movements4 = new Movements(bot4, mcData);
    movements4.canDig = false;
    movements4.allow1by1towers = false;
    movements4.placeCost = 999;
    bot4.pathfinder.setMovements(movements4);

    bot4.globalTickCounter = 0;
    bot4.stuckTickCounter = 0;
    bot4.stuckPosList = [];

    function onTick() {
        bot1.globalTickCounter++;
        if (bot1.pathfinder.isMoving()) {
            bot1.stuckTickCounter++;
            if (bot1.stuckTickCounter >= 100) {
                onStuck(1.5);
                bot1.stuckTickCounter = 0;
            }
        }
    }

    function onTick0() {
        bot0.globalTickCounter++;
        if (bot0.pathfinder.isMoving()) {
            bot0.stuckTickCounter++;
            if (bot0.stuckTickCounter >= 100) {
                onStuck(1.5);
                bot0.stuckTickCounter = 0;
            }
        }
    }

    function onTick2() {
        bot2.globalTickCounter++;
        if (bot2.pathfinder.isMoving()) {
            bot2.stuckTickCounter++;
            if (bot2.stuckTickCounter >= 100) {
                onStuck2(1.5);
                bot2.stuckTickCounter = 0;
            }
        }
    }

    function onTick3() {
        bot3.globalTickCounter++;
        if (bot3.pathfinder.isMoving()) {
            bot3.stuckTickCounter++;
            if (bot3.stuckTickCounter >= 100) {
                onStuck3(1.5);
                bot3.stuckTickCounter = 0;
            }
        }
    }

    function onTick4() {
        bot4.globalTickCounter++;
        if (bot4.pathfinder.isMoving()) {
            bot4.stuckTickCounter++;
            if (bot4.stuckTickCounter >= 100) {
                onStuck4(1.5);
                bot4.stuckTickCounter = 0;
            }
        }
    }

    bot0.on("physicTick", onTick0);
    bot1.on("physicTick", onTick);
    bot2.on("physicTick", onTick2);
    bot3.on("physicTick", onTick3);
    bot4.on("physicTick", onTick4);
   
    // initialize fail count
    let _craftItemFailCount = 0;
    let _killMobFailCount = 0;
    let _mineBlockFailCount = 0;
    let _placeItemFailCount = 0;
    let _smeltItemFailCount = 0;

    // Retrieve array form post bod
    const code = req.body.code;
    const programs = req.body.programs;
    bot1.cumulativeObs = [];
    await bot1.waitForTicks(bot1.waitTicks);
    const r = await evaluateCode(code, programs);
    process.off("uncaughtException", otherError);
    if (r !== "success") {
        bot1.emit("error", handleError(r));
    }
    // await returnItems();
    // wait for last message
    await bot1.waitForTicks(bot1.waitTicks);
    if (!response_sent) {
        response_sent = true;
        res.json({bot0: bot0.observe(), bot1: bot1.observe(), bot2: bot2.observe(), bot3: bot3.observe(), bot4: bot4.observe()});
    }
    bot0.removeListener("physicTick", onTick0);
    bot1.removeListener("physicTick", onTick);
    bot2.removeListener("physicTick", onTick2);
    bot3.removeListener("physicTick", onTick3);
    bot4.removeListener("physicTick", onTick4);

    async function evaluateCode(code, programs) {

        const lines = code.split(";").filter(line => line.trim() !== '');
        const actions = lines.map((line, index) => {
            const completeCode = `
                (async () => {
                    ${programs}
                    return (async () => { ${line} })();
                })()
            `;
    
            return eval(completeCode)
                .catch(error => {
                    console.error(`Action ${index + 1} failed:`, error);
                    console.error(`Failed code block: ${code}\nFailed line: ${line.trim()}`);
                });
        });
    
        await Promise.all(actions);
        return "success";
    }

    function onStuck(posThreshold) {
        const currentPos = bot1.entity.position;
        bot1.stuckPosList.push(currentPos);

        // Check if the list is full
        if (bot1.stuckPosList.length === 5) {
            const oldestPos = bot1.stuckPosList[0];
            const posDifference = currentPos.distanceTo(oldestPos);

            if (posDifference < posThreshold) {
                teleportBot(); // execute the function
            }

            // Remove the oldest time from the list
            bot1.stuckPosList.shift();
        }
    }
    function onStuck0(posThreshold) {
        const currentPos = bot0.entity.position;
        bot0.stuckPosList.push(currentPos);

        // Check if the list is full
        if (bot0.stuckPosList.length === 5) {
            const oldestPos = bot0.stuckPosList[0];
            const posDifference = currentPos.distanceTo(oldestPos);

            if (posDifference < posThreshold) {
                teleportBot0(); // execute the function
            }

            // Remove the oldest time from the list
            bot0.stuckPosList.shift();
        }
    }
    function onStuck2(posThreshold) {
        const currentPos = bot2.entity.position;
        bot2.stuckPosList.push(currentPos);

        // Check if the list is full
        if (bot2.stuckPosList.length === 5) {
            const oldestPos = bot2.stuckPosList[0];
            const posDifference = currentPos.distanceTo(oldestPos);

            if (posDifference < posThreshold) {
                teleportBot2(); // execute the function
            }

            // Remove the oldest time from the list
            bot2.stuckPosList.shift();
        }
    }
    function onStuck3(posThreshold) {
        const currentPos = bot3.entity.position;
        bot3.stuckPosList.push(currentPos);

        // Check if the list is full
        if (bot3.stuckPosList.length === 5) {
            const oldestPos = bot3.stuckPosList[0];
            const posDifference = currentPos.distanceTo(oldestPos);

            if (posDifference < posThreshold) {
                teleportBot3(); // execute the function
            }

            // Remove the oldest time from the list
            bot3.stuckPosList.shift();
        }
    }
    function onStuck4(posThreshold) {
        const currentPos = bot4.entity.position;
        bot4.stuckPosList.push(currentPos);

        // Check if the list is full
        if (bot4.stuckPosList.length === 5) {
            const oldestPos = bot4.stuckPosList[0];
            const posDifference = currentPos.distanceTo(oldestPos);

            if (posDifference < posThreshold) {
                teleportBot4(); // execute the function
            }

            // Remove the oldest time from the list
            bot4.stuckPosList.shift();
        }
    }

    function teleportBot() {
        const blocks = bot1.findBlocks({
            matching: (block) => {
                return block.type === 0;
            },
            maxDistance: 1,
            count: 27,
        });

        if (blocks) {
            // console.log(blocks.length);
            const randomIndex = Math.floor(Math.random() * blocks.length);
            const block = blocks[randomIndex];
            bot1.chat(`/tp @s ${block.x} ${block.y} ${block.z}`);
        } else {
            bot1.chat("/tp @s ~ ~1.25 ~");
        }
    }
    function teleportBot0() {
        const blocks = bot0.findBlocks({
            matching: (block) => {
                return block.type === 0;
            },
            maxDistance: 1,
            count: 27,
        });

        if (blocks) {
            // console.log(blocks.length);
            const randomIndex = Math.floor(Math.random() * blocks.length);
            const block = blocks[randomIndex];
            bot0.chat(`/tp @s ${block.x} ${block.y} ${block.z}`);
        } else {
            bot0.chat("/tp @s ~ ~1.25 ~");
        }
    }

    function teleportBot2() {
        const blocks = bot2.findBlocks({
            matching: (block) => {
                return block.type === 0;
            },
            maxDistance: 1,
            count: 27,
        });

        if (blocks) {
            // console.log(blocks.length);
            const randomIndex = Math.floor(Math.random() * blocks.length);
            const block = blocks[randomIndex];
            bot2.chat(`/tp @s ${block.x} ${block.y} ${block.z}`);
        } else {
            bot2.chat("/tp @s ~ ~1.25 ~");
        }
    }
    function teleportBot3() {
        const blocks = bot3.findBlocks({
            matching: (block) => {
                return block.type === 0;
            },
            maxDistance: 1,
            count: 27,
        });

        if (blocks) {
            // console.log(blocks.length);
            const randomIndex = Math.floor(Math.random() * blocks.length);
            const block = blocks[randomIndex];
            bot3.chat(`/tp @s ${block.x} ${block.y} ${block.z}`);
        } else {
            bot3.chat("/tp @s ~ ~1.25 ~");
        }
    }

    function teleportBot4() {
        // Intentially do nothing
    }

    function handleError(err) {
        let stack = err.stack;
        if (!stack) {
            return err;
        }
        console.log(stack);
        const final_line = stack.split("\n")[1];
        const regex = /<anonymous>:(\d+):\d+\)/;

        const programs_length = programs.split("\n").length;
        let match_line = null;
        for (const line of stack.split("\n")) {
            const match = regex.exec(line);
            if (match) {
                const line_num = parseInt(match[1]);
                if (line_num >= programs_length) {
                    match_line = line_num - programs_length;
                    break;
                }
            }
        }
        if (!match_line) {
            return err.message;
        }
        let f_line = final_line.match(
            /\((?<file>.*):(?<line>\d+):(?<pos>\d+)\)/
        );
        if (f_line && f_line.groups && fs.existsSync(f_line.groups.file)) {
            const { file, line, pos } = f_line.groups;
            const f = fs.readFileSync(file, "utf8").split("\n");
            // let filename = file.match(/(?<=node_modules\\)(.*)/)[1];
            let source = file + `:${line}\n${f[line - 1].trim()}\n `;

            const code_source =
                "at " +
                code.split("\n")[match_line - 1].trim() +
                " in your code";
            return source + err.message + "\n" + code_source;
        } else if (
            f_line &&
            f_line.groups &&
            f_line.groups.file.includes("<anonymous>")
        ) {
            const { file, line, pos } = f_line.groups;
            let source =
                "Your code" +
                `:${match_line}\n${code.split("\n")[match_line - 1].trim()}\n `;
            let code_source = "";
            if (line < programs_length) {
                source =
                    "In your program code: " +
                    programs.split("\n")[line - 1].trim() +
                    "\n";
                code_source = `at line ${match_line}:${code
                    .split("\n")
                    [match_line - 1].trim()} in your code`;
            }
            return source + err.message + "\n" + code_source;
        }
        return err.message;
    }
    
});

app.post("/stop", (req, res) => {
    bot0.end();
    bot1.end();
    bot2.end();
    bot3.end();
    bot4.end()
    res.json({
        message: "Bot stopped",
    });
});

app.post("/pause", (req, res) => {
    if (!bot1 || !bot2) {
        res.status(400).json({ error: "Bot not spawned" });
        return;
    }
    bot1.chat("/pause");
    bot1.waitForTicks(bot1.waitTicks).then(() => {
        res.json({ message: "Success" });
    });
});

app.post("/render", async (req, res) => {
    try {
        // Capture screenshots
        const [screenshot0, screenshot1, screenshot2, screenshot3, screenshot4] = await Promise.all([
            bot0_viewer.render(),
            bot1_viewer.render(),
            bot2_viewer.render(),
            bot3_viewer.render(),
            bot4_viewer.render()
        ]);

        // Convert buffers to Base64 strings
        const image0 = screenshot0.toString('base64');
        const image1 = screenshot1.toString('base64');
        const image2 = screenshot2.toString('base64');
        const image3 = screenshot3.toString('base64');
        const image4 = screenshot4.toString('base64');

        // Send all images in the response
        res.status(200).json({
            message: "Success",
            images: {
                'bot0': image0,
                'bot1': image1,
                'bot2': image2,
                'bot3': image3,
                'bot4': image4
            }
        });
    } catch (error) {
        console.error('Error during rendering:', error);
        res.status(500).json({ message: "Error during rendering", error: error.toString() });
    }
});

// Server listening to PORT 3000

const DEFAULT_PORT = 3000;
const PORT = process.argv[2] || DEFAULT_PORT;
app.listen(PORT, () => {
    console.log(`Server started on port ${PORT}`);
});
