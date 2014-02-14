
App.ApplicationController = require("./application");
App.ActivityLogController = require("./activitylog");
App.TaskController = require("./task");
App.TasksController = require("./tasks");
App.MobileTasksController = require("./mobileTasks");
App.CompletedController = require("./completed");
App.CompletedTaskController = require("./completedTask");
App.AboutController = require("./about");
App.ApiAccessController = require("./api_access");
App.SynchronizationController = require("./synchronization");
App.ConfigureController = require("./configure");
App.SmsController = require("./sms");
App.EditTaskController = require("./editTask");
App.CreateTaskController = require("./createTask");
App.CreateTaskModalController = require("./editTask");
App.CreateAnnotationController = require("./create_annotation");
App.TermsOfServiceController = require("./termsOfService");

App.IndexController = Ember.Controller.extend({
  needs: ["application"],
  init: function(){
    var user = this.get('controllers.application').user;
    var configured = user.configured;
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
                self.get('controllers.application').update_user_info();
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
