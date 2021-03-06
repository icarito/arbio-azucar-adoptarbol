module.exports = {
  /*
  ** Headers of the page
  */
  head: {
    title: 'adopta-arbol',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: 'Sistema de adopción' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
      { rel: 'stylesheet', href: '/static/blaze.min.css' },
      { rel: 'stylesheet', href: '/static/font-awesome.min.css' }
    ],
    script: [
      { src: '/static/inobounce.min.js' }
    ]
  },
  /*
  ** Customize the progress bar color
  */
  loading: { color: '#3B8070' },
  /*
  ** Build configuration
  */
  mode: 'spa',
  build: {
    /*
    ** Run ESLint on save
    */
    extend (config, { isDev, isClient }) {
      if (isDev && isClient) {
        config.module.rules.push({
          enforce: 'pre',
          test: /\.(js|vue)$/,
          loader: 'eslint-loader',
          exclude: /(node_modules)/
        })
      }
    }
  },
  modules: [
    '@nuxtjs/axios'
  ],
  axios: {
    baseURL: '/api'
    // proxyHeaders: false
  }
}
