var view = Ember.View.extend({
    didInsertElement: function() {
        var controller = this.get('controller');
        controller.get('bindKeyboardEvents').bind(controller)();
    }
});

module.exports = view;
