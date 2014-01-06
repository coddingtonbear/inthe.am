
App.ApplicationController = require("./application");
App.NavigationController = require("./navigation");
App.TaskController = require("./task");
App.TasksController = require("./tasks");
App.CompletedController = require("./completed");
App.CompletedTaskController = require("./completedTask");

App.IndexController = Ember.Controller.extend({
  needs: ["application"],
  init: function(){
    var user = this.get('controllers.application').user;
    var configured = user.dropbox_configured;
    var self = this;
    if (! user.logged_in) {
      self.transitionToRoute('about');
    } else {
      if (configured) {
        self.transitionToRoute('tasks');
      } else {
        $.ajax(
          {
            url: '/api/v1/task/autoconfigure/',
            dataType: 'json',
            statusCode: {
              200: function(){
                self.transitionToRoute('tasks');
              },
              404: function(){
                self.transitionToRoute('unconfigurable');
              },
              409: function(){
                self.transitionToRoute('configure');
              },
            }
          }
        );
      }
    }
  }
});
