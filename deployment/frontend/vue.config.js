module.exports = {
  transpileDependencies: [],
  configureWebpack: {
    plugins: []
  },
  chainWebpack: config => {
    config.plugins.delete('progress')
    config.plugins.delete('simple-progress')
  }
}
