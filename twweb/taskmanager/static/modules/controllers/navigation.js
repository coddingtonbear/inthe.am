var controller = Ember.Controller.extend({
  needs: ["application", "tasks"],

  actions: {
    'logout': function(){
      window.location.href=this.get('controllers.application').urls.logout;
    },
    'login': function(){
      window.location.href=this.get('controllers.application').urls.login;
    },
  }
});

module.exports = controller;
