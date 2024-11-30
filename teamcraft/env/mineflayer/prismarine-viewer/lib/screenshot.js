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
  
  module.exports = (bot, {botId = 0, viewDistance = 16, output = '/Voyager/data/', width = 512, height = 512, compressionLevel = 6}) => {
    const canvas = createCanvas(width, height)
    const renderer = new THREE.WebGLRenderer({ canvas })
    const viewer = new Viewer(renderer)
  
    const framesDir = path.join(output, botId.toString());
    if (!fs.existsSync(framesDir)) {
      fs.mkdirSync(framesDir, { recursive: true });
    }
  
    if (!viewer.setVersion(bot.version)) {
      return false
    }
    viewer.setFirstPersonCamera(bot.entity.position, bot.entity.yaw, bot.entity.pitch)
  
    const worldView = new WorldView(bot.world, viewDistance, bot.entity.position)
    viewer.listen(worldView)
    worldView.init(bot.entity.position)
  
    function botPosition () {
      viewer.setFirstPersonCamera(bot.entity.position, bot.entity.yaw, bot.entity.pitch)
      worldView.updatePosition(bot.entity.position)
    }
  
    function takeScreenshot() {
      return new Promise((resolve, reject) => {
          viewer.update();
          renderer.render(viewer.scene, viewer.camera);

          const timestamp = new Date().toISOString().slice(0, -1).replace(/:/g, '').replace('.', '').replace('T', '_');
          const frameFileName = path.join(framesDir, `screenshot_${timestamp}.png`);

          const imageStream = canvas.createPNGStream({
            bufsize: 4096,
            compressionLevel: compressionLevel, // Adjust compression level (0-9, 6 is typical)
            progressive: false
          });
          const fileStream = fs.createWriteStream(frameFileName);
          imageStream.pipe(fileStream);

          fileStream.on('finish', () => {
              console.log(`Screenshot saved as ${frameFileName}`);
              resolve(frameFileName);
          });

          fileStream.on('error', error => {
              console.error('Error capturing screenshot:', error);
              reject(error);
          });
      });
  }
      
  
    // Register events
    bot.on('move', botPosition)
    worldView.listenToBot(bot)
  
    return {takeScreenshot};
  }
  