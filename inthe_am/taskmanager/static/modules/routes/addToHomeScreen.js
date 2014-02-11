var route = Ember.Route.extend({
  afterModel: function(tasks, transition) {
    if (window.navigator.standalone) {
      this.transitionTo('mobileTasks');
    }
  }
});

module.exports = route;
