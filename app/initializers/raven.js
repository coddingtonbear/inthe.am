export default {
  name: 'raven',
  initialize: function (application) {
    Raven.config(
            'https://7659aef75d244f8ab30c3071c8d3af52@sentry.io/210057',
      {
        whitelistUrls: [/inthe\.am/]
      }
        ).addPlugin(Raven.Plugins.Ember).install()
  }
}
