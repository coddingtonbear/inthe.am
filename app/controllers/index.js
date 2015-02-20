import Ember from "ember";

var controller = Ember.Controller.extend({
    needs: ["application"],
    init: function(){
        var application = this.get('controllers.application');
        var user = application.user;
        if(user.logged_in) {
            if(application.isSmallScreen()) {
                this.transitionToRoute('mobile-tasks');
            } else {
                this.transitionToRoute('tasks');
            }
        }
    }
});

export default controller;
