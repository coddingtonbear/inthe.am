import Ember from "ember";

var route = Ember.Route.extend({
    model: function() {
        return this.store.findAll('task');
    },
    afterModel: function(tasks, transition) {
        if (transition.targetName === "tasks.index" || transition.targetName === "tasks") {
            if($(document).width() > 700) {
                Ember.run.next(this, function(){
                    var task = this.controllerFor('tasks')
                            .get('pendingTasks.firstObject');
                    if(task) {
                            this.transitionTo('task', tasks.get('firstObject'));
                    }
                });
            } else {
                this.transitionToRoute('mobile-tasks');
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

export default route;
