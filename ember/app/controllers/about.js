import Ember from 'ember'

var controller = Ember.Controller.extend({
  urls: {
    web_ui: '/web_ui.png'
  },
  applicationController: Ember.inject.controller('application'),
  actions: {
    login: function () {
      window.location = this.get('applicationController.urls.login')
    }
  }
})

export default controller
