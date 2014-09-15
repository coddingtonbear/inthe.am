App.Router.map(function(){
  this.route("login", {path: "/login"});
  this.route("about", {path: "/about"});
  this.resource("addToHomeScreen", {path: "/add-to-home-screen"});
  this.resource("mobileTasks", {path: "/mobile-tasks"});
  this.route("createTask", {path: "/create-task"});
  this.route("editTask", {path: "/edit-task/:uuid"});
  this.route("annotateTask", {path: "/annotate-task"});
  this.resource("tasks", function(){
    this.resource("task", {path: "/:uuid"});
  });
  this.resource("completed", function(){
    this.resource("completedTask", {path: "/:uuid"});
  });
  this.resource("activityLog", {path: "/activity-log"});
  this.route("unconfigurable", {path: "/no-tasks"});
  this.route("configure", {path: "/configure"});
  this.route("getting_started", {path: "/getting-started"});
  this.route("termsOfService", {path: "/terms-of-service"});
  this.route("fourOhFour", {path: "*path"});
});

App.Router.reopen({
  location: 'history'
});
