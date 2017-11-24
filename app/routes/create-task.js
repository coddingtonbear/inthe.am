import Ember from 'ember'

var route = Ember.Route.extend({
  setupController: function (controller) {
    var model = this.store.createRecord('task', {})
    controller.set('model', model)
  },
  actions: {
    error: function (reason, tsn) {
      var application = this.controllerFor('application')
      application.get('handleError').bind(application)(reason, tsn)
    }
  }
})

export default route
