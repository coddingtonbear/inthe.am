import Ember from "ember";

var controller = Ember.Controller.extend({
    needs: ["application"],
    init: function(){
        var user = this.get('controllers.application').user;
        var configured = user.configured;
        var self = this;
        if (user.logged_in) {
            self.transitionToRoute('tasks');
        }
    }
});

export default controller;
