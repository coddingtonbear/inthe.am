var route = Ember.Route.extend({
  model: function() {
    return this.store.all('task');
  },
  afterModel: function(tasks, transition) {
    if (transition.targetName == "tasks.index") {
      if($(document).width() > 700) {
        Ember.run.next(this, function(){
            var task = this.controllerFor('tasks')
                .get('pendingTasks.firstObject');
            if(task) {
                this.transitionTo('task', tasks.get('firstObject'));
            }
        })
      } else {
        if (window.navigator.standalone || window.navigator.userAgent.indexOf('iPhone') === -1) {
          this.transitionTo('mobileTasks');
        } else {
          this.transitionTo('addToHomeScreen');
        }
      }
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
