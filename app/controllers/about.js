import Ember from "ember";

var controller = Ember.Controller.extend({
    needs: ['application'],
    urls: {
        web_ui: '/web_ui.png',
    },
    actions: {
        login: function(){
            window.location = this.get('controllers.application.urls.login');
        },
    }
});

export default controller;
