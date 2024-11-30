global.THREE = require('three')
global.Worker = require('worker_threads').Worker
const { createCanvas } = require('node-canvas-webgl/lib')
const { WorldView, Viewer } = require('prismarine-viewer/viewer')


module.exports = (bot, {viewDistance = 16, width = 1920, height = 1080, compressionLevel = 6}) => {
  
  const canvas = createCanvas(width, height)
  const renderer = new THREE.WebGLRenderer({ canvas })
  const viewer = new Viewer(renderer)

  if (!viewer.setVersion(bot.version)) {
    throw new Error(`Failed to set version`);
  }
  viewer.setFirstPersonCamera(bot.entity.position, bot.entity.yaw, bot.entity.pitch)

  const worldView = new WorldView(bot.world, viewDistance, bot.entity.position)
  viewer.listen(worldView)
  worldView.init(bot.entity.position)

  function botPosition () {
    viewer.setFirstPersonCamera(bot.entity.position, bot.entity.yaw, bot.entity.pitch)
    worldView.updatePosition(bot.entity.position)
  }

  function render() {
    return new Promise((resolve, reject) => {
        
      viewer.update();
      renderer.render(viewer.scene, viewer.camera);

      const imageStream = canvas.createPNGStream({
        bufsize: 4096,
        compressionLevel: compressionLevel, // Adjust compression level (0-9, 6 is typical)
        progressive: false
      });
      const chunks = [];

      imageStream.on('data', chunk => {
        chunks.push(chunk);
      });
  
      imageStream.on('end', () => {
        const imageBuffer = Buffer.concat(chunks);
        resolve(imageBuffer);
      });
  
      imageStream.on('error', error => {
        console.error('Error capturing screenshot:', error);
        reject(error);

      });
    });
}
    
  // Register events
  bot.on('move', botPosition)
  worldView.listenToBot(bot)

  return {render};
}
  