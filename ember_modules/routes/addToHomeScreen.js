var route = Ember.Route.extend({
    afterModel: function(tasks, transition) {
        if($(document).width() > 700) {
            this.transitionTo('about');
        } else if (window.navigator.standalone) {
            this.transitionTo('mobileTasks');
        }
    }
});

module.exports = route;
