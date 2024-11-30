module.exports = {
  mineflayer: require('./lib/mineflayer'),
  standalone: require('./lib/standalone'),
  headless: require('./lib/headless'),
  screenshot: require('./lib/screenshot'),
  render: require('./lib/render'),
  viewer: require('./viewer'),
  supportedVersions: require('./viewer').supportedVersions
}
