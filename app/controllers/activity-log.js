import Ember from "ember";

var controller = Ember.ArrayController.extend({
    refresh: function(){
        try {
            this.get('content').update();
        } catch (e) {
            // Nothing to worry about -- probably just not loaded.
        }
    },
});

export default controller;
