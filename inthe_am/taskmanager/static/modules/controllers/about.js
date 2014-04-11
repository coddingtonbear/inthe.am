var controller = Ember.Controller.extend({
  needs: ['application'],
  urls: {
    web_ui: '/static/about/web_ui.png',
    mobile: '/static/about/mobile.png'
  },
  actions: {
    login: function(){
      window.location = this.get('controllers.application.urls.login');
    },
  }
});

module.exports = controller;
