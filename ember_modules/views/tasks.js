var view = Ember.View.extend({
    didInsertElement: function() {
        Ember.run.next(this, function(){
            var controller = this.get('controller');
            var handleChanged = function() {
                controller.set('filterString', this.value);
                controller.notifyPropertyChange('pendingTasks');
            }
            var element = $('.filter-string-element');
            element.on('input', handleChanged);
            element.on('search', handleChanged);
        });
    }
});

module.exports = view;
