var route = Ember.Route.extend({
  model: function() {
    return this.store.find('task');
  },
  beforeModel: function(tasks, transition) {
    var application = this.controllerFor('application');
    if(application.user.logged_in && !application.user.tos_up_to_date) {
      this.transitionTo('termsOfService');
    }
  },
  afterModel: function(tasks, transition) {
    if (tasks.get('length') === 0) {
      this.transitionTo('getting_started');
    } else if (transition.targetName == "tasks.index") {
      if($(document).width() > 700) {
        this.transitionTo('task', tasks.get('firstObject'));
      } else {
        if (window.navigator.standalone) {
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
