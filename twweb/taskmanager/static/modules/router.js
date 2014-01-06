App.Router.map(function(){
  this.route("login", {path: "/login"});
  this.route("about", {path: "/about"});
  this.resource("tasks", function(){
    this.resource("task", {path: "/:uuid"});
  });
  this.route("unconfigurable", {path: "/no-tasks"});
  this.route("configure", {path: "/configure"});
});

App.Router.reopen({
  location: 'history'
});
