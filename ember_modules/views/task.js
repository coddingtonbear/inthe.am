var view = Ember.View.extend({
    taskObserver: function() {
        $('#task-details').scrollTop(0);
    }.observes('controller.model'),
});

module.exports = view;
