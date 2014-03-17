var route = Ember.Route.extend({
  model: function(params) {
    return this.store.find('task', params.uuid);
  },
  actions: {
    error: function(reason, tsn) {
      var application = this.controllerFor('application');
      application.get('handleError').bind(application)(reason, tsn);
    }
  }
});

module.exports = route;
