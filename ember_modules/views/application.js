var view = Ember.View.extend({
    bodyEvents: {
        'chardinJs:stop': '_help_hidden'
    },
    didInsertElement: function() {
        var controller = this.get('controller');
        controller.get('bindKeyboardEvents').bind(controller)();

        // Bind select body events to ApplicationController
        for (var eventName in this.bodyEvents) {
            if (this.bodyEvents.hasOwnProperty(eventName)) {
                $('body').bind(eventName, function(actionName, evt) {
                    controller.send(actionName, evt);
                }.bind(this, this.bodyEvents[eventName]));
            }
        }
    }
});

module.exports = view;
