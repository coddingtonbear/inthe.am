import Ember from "ember";

var controller = Ember.Controller.extend({
    needs: ["application"],
    init: function(){
        var user = this.get('controllers.application').user;
        if(user.logged_in) {
            this.transitionToRoute('tasks');
        }
    }
});

export default controller;
