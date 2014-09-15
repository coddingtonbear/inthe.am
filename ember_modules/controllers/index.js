
App.ApplicationController = require("./application");
App.ActivityLogController = require("./activitylog");
App.TaskController = require("./task");
App.TasksController = require("./tasks");
App.MobileTasksController = require("./mobileTasks");
App.CompletedController = require("./completed");
App.CompletedTaskController = require("./completedTask");
App.AboutController = require("./about");
App.ConfigureController = require("./configure");
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
      self.transitionToRoute('tasks');
    }
  }
});
