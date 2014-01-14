var route = Ember.Route.extend({
  model: function(){
    return this.store.findQuery('task', {completed: 0});
  },
  afterModel: function(tasks, transition) {
    if (tasks.get('length') === 0) {
      this.transitionTo('getting_started');
    }
  }
});

module.exports = route;
