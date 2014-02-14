
App.IndexRoute = Ember.Route.extend({
  renderTemplate: function() {
    this.render('index');
  }
});
App.TaskRoute = require("./task");
App.TasksRoute = require("./tasks");
App.TasksIndexRoute = require("./tasks");
App.MobileTasksRoute = require("./mobileTasks");
App.CompletedRoute = require("./completed");
App.CompletedTaskRoute = require("./completedTask");
App.ActivityLogRoute = require("./activitylog");
App.ApplicationRoute = require("./application");
App.AddToHomeScreenRoute = require("./addToHomeScreen");
App.ErrorRoute = require("./error");
App.CreateTaskRoute = require("./createTask");
