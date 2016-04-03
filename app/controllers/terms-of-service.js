import Ember from "ember";

var controller = Ember.Controller.extend({
    applicationController: Ember.inject.controller('application'),
    actions: {
        accept: function(version) {
            return this.get('applicationController').ajaxRequest({
                url: this.get('applicationController').urls.tos_accept,
                type: 'POST',
                data: {
                    version: version
                },
            }).then(function(){
                this.get('applicationController').update_user_info();
                this.get('applicationController').handlePostLoginRedirects();
                this.transitionToRoute('getting-started');
            }.bind(this), function(msg){
                this.get('applicationController').error_message(
                    `An error was encountered while ` +
                    `attempting to accept the terms of service: ${msg}`
                );
            }.bind(this));
        }
    }
});

export default controller;
