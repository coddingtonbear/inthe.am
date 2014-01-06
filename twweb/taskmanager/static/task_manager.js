(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);throw new Error("Cannot find module '"+o+"'")}var f=n[o]={exports:{}};t[o][0].call(f.exports,function(e){var n=t[o][1][e];return s(n?n:e)},f,f.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
var App = Ember.Application.create({
  LOG_TRANSITIONS: true
});

App.ApplicationAdapter = DS.DjangoTastypieAdapter.extend({
  namespace: 'api/v1'
});

module.exports = App;

},{}],2:[function(require,module,exports){
var controller = Ember.Controller.extend({
  user: null,
  urls: {
    logout: '/logout/',
    login: '/login/dropbox/'
  },
  init: function(){
    this.set(
      'user',
      JSON.parse(
        $.ajax(
          {
            url: '/api/v1/user/status/',
            async: false,
            dataType: 'json'
          }
        ).responseText
      )
    );
  }
});

module.exports = controller;

},{}],3:[function(require,module,exports){

App.ApplicationController = require("./application");
App.NavigationController = require("./navigation");
App.TaskController = require("./task");
App.TasksController = require("./tasks");

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

},{"./application":2,"./navigation":4,"./task":5,"./tasks":6}],4:[function(require,module,exports){
var controller = Ember.Controller.extend({
  needs: ["application", "tasks"],

  actions: {
    'logout': function(){
      window.location.href=this.get('controllers.application').urls.logout;
    },
    'login': function(){
      window.location.href=this.get('controllers.application').urls.login;
    }
  }
});

module.exports = controller;

},{}],5:[function(require,module,exports){
var controller = Ember.ObjectController.extend();

module.exports = controller;

},{}],6:[function(require,module,exports){
var controller = Ember.ArrayController.extend({
  sortProperties: ['urgency'],
  sortAscending: false,

  taskCount: function(){
    return this.get('model.length');
  }.property('@each'),

  actions: {
    view_task: function(task){
      this.transitionToRoute('task', task);
    }
  }
});

module.exports = controller;

},{}],7:[function(require,module,exports){

},{}],8:[function(require,module,exports){
window.App = require('./app');

require("./controllers");
require("./models");
require("./routes");
require("./views");
require("./helpers");

},{"./app":1,"./controllers":3,"./helpers":7,"./models":9,"./routes":13,"./views":16}],9:[function(require,module,exports){

App.User = require("./user.js");
App.Task = require("./task.js");

},{"./task.js":10,"./user.js":11}],10:[function(require,module,exports){
var model = DS.Model.extend({
  description: DS.attr('string'),
  due: DS.attr('date'),
  entry: DS.attr('date'),
  modified: DS.attr('date'),
  priority: DS.attr('string'),
  resource_uri: DS.attr('string'),
  start: DS.attr('date'),
  'status': DS.attr('string'),
  urgency: DS.attr('number'),
  uuid: DS.attr('string')
});

module.exports = model;

},{}],11:[function(require,module,exports){
var model = DS.Model.extend({
  logged_in: DS.attr('boolean'),
  uid: DS.attr('string'),
  email: DS.attr('string'),
  dropbox_configured: DS.attr('boolean'),
});

module.exports = model;

},{}],12:[function(require,module,exports){
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

},{}],13:[function(require,module,exports){

App.IndexRoute = Ember.Route.extend({
  renderTemplate: function() {
    this.render('index');
    this.render('navigation', {outlet: 'navigation'});
  }
});
App.TasksRoute = require("./tasks");
App.TaskRoute = require("./task");

},{"./task":14,"./tasks":15}],14:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(params) {
    return this.store.find('task', params.uuid);
  }
});

module.exports = route;

},{}],15:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(){
    return this.store.find('task');
  }
});

module.exports = route;

},{}],16:[function(require,module,exports){

App.NavigationView = require("./navigation");

},{"./navigation":17}],17:[function(require,module,exports){
var view = Ember.View.extend();

module.exports = view;

},{}]},{},[1,7,8,12])