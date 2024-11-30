/* global THREE */
function safeRequire (path) {
  try {
    return require(path)
  } catch (e) {
    return {}
  }
}
const { spawn } = require('child_process')
const net = require('net')
global.THREE = require('three')
global.Worker = require('worker_threads').Worker
const { createCanvas } = require('node-canvas-webgl/lib')
const { WorldView, Viewer, getBufferFromStream } = require('../viewer')
const fs = require('fs');
const path = require('path');
let frameIndex = 0



module.exports = (bot, { agentId, viewDistance = 6, output = '/Voyager/voyager/data/build_0/frames', frames = -1, width = 512, height = 512, logFFMPEG = false, jpegOptions }) => {
  const canvas = createCanvas(width, height)
  const renderer = new THREE.WebGLRenderer({ canvas })
  const viewer = new Viewer(renderer)
  let image_index = 0


  // Define the directory where to save the frames
  const framesDir = path.join(output, agentId.toString());
  if (!fs.existsSync(framesDir)) {
    fs.mkdirSync(framesDir, { recursive: true });
  }

  if (!viewer.setVersion(bot.version)) {
    return false
  }
  viewer.setFirstPersonCamera(bot.entity.position, bot.entity.yaw, bot.entity.pitch)

  // Load world
  const worldView = new WorldView(bot.world, viewDistance, bot.entity.position)
  viewer.listen(worldView)
  worldView.init(bot.entity.position)

  function botPosition () {
    viewer.setFirstPersonCamera(bot.entity.position, bot.entity.yaw, bot.entity.pitch)
    worldView.updatePosition(bot.entity.position)
  }

  // TODO: Temp Solve of output path issue
  const ffmpegOutput = true
  let client = null

 if (ffmpegOutput) {
    client = spawn('ffmpeg', ['-y', '-i', 'pipe:0', output])
    if (logFFMPEG) {
      client.stdout.on('data', (data) => {
        console.log(`stdout: ${data}`)
      })

      client.stderr.on('data', (data) => {
        console.error(`stderr: ${data}`)
      })
    }
    update()
  }

  // Force end of stream
  bot.on('end', () => { frames = 0 })



  function update() {
    viewer.update();
    renderer.render(viewer.scene, viewer.camera);

    // const frameFileName = path.join(framesDir, `frame_${image_index.toString().padStart(4, '0')}.jpg`);

    // TODO: temp solution for time recording
    // Generate a timestamp string in the format of "YYYY-MM-DD_HHMMSSmmm"
    const timestamp = new Date().toISOString().slice(0, -1).replace(/:/g, '').replace('.', '').replace('T', '_');
    // Include the timestamp in the frame file name
    const frameFileName = path.join(framesDir, `frame_${image_index.toString().padStart(4, '0')}_${timestamp}.jpg`);




    const imageStream = canvas.createJPEGStream({
      bufsize: 4096,
      quality: 0.9, // Adjust as needed
      progressive: false,
      ...jpegOptions
    });

    const fileStream = fs.createWriteStream(frameFileName);
    imageStream.pipe(fileStream);

    fileStream.on('finish', () => {
      frameIndex++;
      image_index++;
      if (frameIndex < frames || frames < 0) {
        setTimeout(update, 16); // Proceed to next frame
      } else {
        console.log(`Finished saving frames for agent ${agentId}`);
      }
    });

    imageStream.on('error', (error) => {
      console.error('Error capturing frame:', error);
    });
  }

  // Register events
  bot.on('move', botPosition)
  worldView.listenToBot(bot)

  return client
}




