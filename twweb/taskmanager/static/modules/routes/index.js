
App.IndexRoute = Ember.Route.extend({
  renderTemplate: function() {
    this.render('index');
    this.render('navigation', {outlet: 'navigation'});
  }
});
App.TasksRoute = require("./tasks");
App.TaskRoute = require("./task");
