import Ember from "ember";

var controller = Ember.Controller.extend({
    needs: ['application'],
    actions: {
        accept: function(version) {
            return this.get('controllers.application').ajaxRequest({
                url: this.get('controllers.application').urls.tos_accept,
                type: 'POST',
                data: {
                    version: version
                },
            }).then(function(){
                this.get('controllers.application').update_user_info();
                this.get('controllers.application').handlePostLoginRedirects();
                this.transitionToRoute('tasks');
            }.bind(this), function(msg){
                this.get('controllers.application').error_message(
                    `An error was encountered while ` +
                    `attempting to accept the terms of service: ${msg}`
                );
            }.bind(this));
        }
    }
});

export default controller;
