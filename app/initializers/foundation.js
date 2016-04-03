import Ember from 'ember';

export default {
    name: "foundation",
    initialize: function(application) {
        Ember.View.reopen({
            _initializeFoundation: function() {
                $(document).foundation();
            },
            initializeFoundation: function() {
                Ember.run.debounce(
                    null,
                    this._initializeFoundation,
                    500
                );
            }.on('didInsertElement'),
        });
    }
};
