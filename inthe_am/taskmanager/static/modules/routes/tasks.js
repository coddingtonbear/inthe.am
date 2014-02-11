var route = Ember.Route.extend({
  model: function() {
    return this.store.find('task');
  },
  afterModel: function(tasks, transition) {
    if (tasks.get('length') === 0) {
      this.transitionTo('getting_started');
    } else if (transition.targetName == "tasks.index") {
      if($(document).width() > 350) {
        this.transitionTo('task', tasks.get('firstObject'));
      } else {
        this.transitionTo('mobileTasks');
      }
    }
  }
});

module.exports = route;
