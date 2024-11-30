const fs = require("fs");
const express = require("express");
const bodyParser = require("body-parser");
const mineflayer = require("mineflayer");
const mineflayerViewer = require('prismarine-viewer').headless;

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

const app = express();

app.use(bodyParser.json({ limit: "50mb" }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: false }));

const bots = [];
let botCount = 5; // You can change this to the number of bots you want

app.post("/start", async (req, res) => {
    if (bots.length > 0) onDisconnect("Restarting bots");
    bots.length = 0;
    console.log(req.body);
    const ip = "localhost";
    console.log("Starting bots..., bot count: ", botCount);
    for (let i = 0; i < botCount; i++) {
        const bot = mineflayer.createBot({
            host: ip, // minecraft server ip
            port: req.body.port, // minecraft server port
            username: `bot${i}`, // minecraft username
            disableChatSigning: true,
            checkTimeoutInterval: 60 * 60 * 1000,
        });

        bot.once("error", onConnectionFailed);

        bot.waitTicks = req.body.waitTicks;
        bot.globalTickCounter = 0;
        bot.stuckTickCounter = 0;
        bot.stuckPosList = [];
        bot.iron_pickaxe = false;
        bot.on("kicked", onDisconnect);

        
        bot.on("mount", () => {
            bot.dismount();
        });

        bots.push(bot);
        global[`bot${i}`] = bot; // Assign dynamic variable name
        console.log(`bot${i} created`);
    }

    console.log('mineflayer index file init...');

    bot4.on('chat', async (username, message) => {
        const args = message.split(' ');
        if (args[0] === 'startRecoding') {
            let frame_duration = parseInt(args[1]);
            let path_name = args[2];
            mineflayerViewer(bot1, { agentId: "1", port: 3007, firstPerson: true ,output: path_name, frames: frame_duration, width: 640, height: 480}) // port is the minecraft server port, if first person is false, you get a bird's-eye view
            mineflayerViewer(bot2, { agentId: "2", port: 3008, firstPerson: true ,output: path_name, frames: frame_duration, width: 640, height: 480}) // port is the minecraft server port, if first person is false, you get a bird's-eye view
            mineflayerViewer(bot3, { agentId: "3", port: 3008, firstPerson: true ,output: path_name, frames: frame_duration, width: 640, height: 480}) // port is the minecraft server port, if first person is false, you get a bird's-eye view
            mineflayerViewer(bot4, { agentId: "4", port: 3008, firstPerson: true ,output: path_name, frames: frame_duration, width: 640, height: 480}) // port is the minecraft server port, if first person is false, you get a bird's-eye view
            bot4.chat("start recording");
        }
    });

    const observations = {};
    await Promise.all(bots.map((bot, index) => new Promise((resolve, reject) => {
        bot.once("spawn", async () => {
            try {
                bot.removeListener("error", onConnectionFailed);
                let itemTicks = 1;

                bot.chat("/clear @s");
                await bot.waitForTicks(bot.waitTicks * 3);
                console.log(index)
                if (index === 0) {
                    console.log("index 0")
                    bot.chat('/time set day');
                    bot.chat('/gamerule doDaylightCycle false');
                    bot.chat('/weather clear');
                    bot.chat('/gamerule doWeatherCycle false');
                }

                const { pathfinder } = require("mineflayer-pathfinder");
                const tool = require("mineflayer-tool").plugin;
                const collectBlock = require("mineflayer-collectblock").plugin;
                const pvp = require("mineflayer-pvp").plugin;
                const minecraftHawkEye = require("minecrafthawkeye");
                bot.loadPlugin(pathfinder);
                bot.loadPlugin(tool);
                bot.loadPlugin(collectBlock);
                bot.loadPlugin(pvp);
                bot.loadPlugin(minecraftHawkEye);

                obs.inject(bot, [
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
                skills.inject(bot);

                if (req.body.spread) {
                    bot.chat(`/spreadplayers ~ ~ 0 300 under 80 false @s`);
                    await bot.waitForTicks(bot.waitTicks);
                }

                await bot.waitForTicks(bot.waitTicks * itemTicks);

                initCounter(bot);
                observations[`bot${index}`] = bot.observe();
                console.log(`bot${index} spawned`);
                resolve();
            } catch (err) {
                console.error(`Error initializing bot ${index}:`, err);
                reject(err);
            }
        });
    })));

    res.json(observations);
    console.log("Bots started", observations);



    function onConnectionFailed(e) {
        console.log(e);
        bots.length = 0;
        res.status(400).json({ error: e });
    }
    function onDisconnect(message) {
        bots.forEach(bot => {
            if (bot.viewer) {
                bot.viewer.close();
            }
            bot.end();
            console.log(message);
        });
        bots.length = 0;
    }
});

app.post("/step", async (req, res) => {
    // import useful package
    console.log(req.body, "step body");
    let response_sent = false;
    function otherError(err) {
        console.log("Uncaught Error");
        bots.forEach(bot => bot.emit("error", handleError(err)));
        bot1.waitForTicks(bot1.waitTicks).then(() => {
            if (!response_sent) {
                response_sent = true;
                const observations = {};
                bots.forEach((bot, index) => {
                    observations[`bot${index}`] = bot.observe();
                });
                res.json(observations);
            }
        });
    }

    process.on("uncaughtException", otherError);

    console.log(bot1.version, "bot1 version")
    const mcData = require("minecraft-data")(bot1.version);
    mcData.itemsByName["leather_cap"] = mcData.itemsByName["leather_helmet"];
    mcData.itemsByName["leather_tunic"] = mcData.itemsByName["leather_chestplate"];
    mcData.itemsByName["leather_pants"] = mcData.itemsByName["leather_leggings"];
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

    // Set up pathfinder for each bot
    bots.forEach(bot => {
        const movements = new Movements(bot, mcData);
        movements.canDig = false;
        movements.allow1by1towers = false;
        movements.placeCost = 999;
        bot.pathfinder.setMovements(movements);
        bot.globalTickCounter = 0;
        bot.stuckTickCounter = 0;
        bot.stuckPosList = [];
        bot.on("physicTick", () => onTick(bot));
    });

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

    await bot1.waitForTicks(bot1.waitTicks);
    if (!response_sent) {
        response_sent = true;
        const observations = {};
        bots.forEach((bot, index) => {
            observations[`bot${index}`] = bot.observe();
        });
        res.json(observations);
    }

    bots.forEach(bot => bot.removeListener("physicTick", () => onTick(bot)));

    // take screenshot
    await bot1.chat('takeScreenshot')
    
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

    function onTick(bot) {
        bot.globalTickCounter++;
        if (bot.pathfinder.isMoving()) {
            bot.stuckTickCounter++;
            if (bot.stuckTickCounter >= 100) {
                onStuck(bot, 1.5);
                bot.stuckTickCounter = 0;
            }
        }
    }

    function onStuck(bot, posThreshold) {
        const currentPos = bot.entity.position;
        bot.stuckPosList.push(currentPos);

        if (bot.stuckPosList.length === 5) {
            const oldestPos = bot.stuckPosList[0];
            const posDifference = currentPos.distanceTo(oldestPos);

            if (posDifference < posThreshold) {
                teleportBot(bot);
            }

            bot.stuckPosList.shift();
        }
    }

    function teleportBot(bot) {
        const blocks = bot.findBlocks({
            matching: (block) => block.type === 0,
            maxDistance: 1,
            count: 27,
        });

        if (blocks) {
            const randomIndex = Math.floor(Math.random() * blocks.length);
            const block = blocks[randomIndex];
            bot.chat(`/tp @s ${block.x} ${block.y} ${block.z}`);
        } else {
            bot.chat("/tp @s ~ ~1.25 ~");
        }
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
    bots.forEach(bot => bot.end());
    bots.length = 0;
    res.json({ message: "Bots stopped" });
});

app.post("/pause", (req, res) => {
    if (bots.length === 0) {
        res.status(400).json({ error: "Bots not spawned" });
        return;
    }
    bots.forEach(bot => bot.chat("/pause"));
    bot1.waitForTicks(bot1.waitTicks).then(() => {
        res.json({ message: "Success" });
    });
});

// Server listening to PORT 3000

const DEFAULT_PORT = 3000;
const PORT = process.argv[2] || DEFAULT_PORT;
app.listen(PORT, () => {
    console.log(`Server started on port ${PORT}`);
});
