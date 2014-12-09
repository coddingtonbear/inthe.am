var route = Ember.Route.extend({
  model: function() {
    return this.store.all('task');
  },
  afterModel: function(tasks, transition) {
    if (transition.targetName == "tasks.index") {
      Ember.run.next(this, function(){
          var task = this.controllerFor('tasks')
              .get('pendingTasks.firstObject');
          if(task) {
              this.transitionTo('task', tasks.get('firstObject'));
          }
      })
    }
  },
  actions: {
    error: function(reason, tsn) {
      var application = this.controllerFor('application');
      application.get('handleError').bind(application)(reason, tsn);
    }
  }
});

module.exports = route;
