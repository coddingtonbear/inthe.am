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
  pending_count: null,
  urls: {
    logout: '/logout/',
    login: '/login/dropbox-oauth2/',
    ca_certificate: '/api/v1/user/ca-certificate/',
    my_certificate: '/api/v1/user/my-certificate/',
    my_key: '/api/v1/user/my-key/',
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
var controller = Ember.ArrayController.extend({
  sortProperties: ['-modified'],
  sortAscending: false,

  actions: {
    view_task: function(task){
      this.transitionToRoute('completedTask', task);
    }
  },
});

module.exports = controller;

},{}],4:[function(require,module,exports){
var controller = Ember.ObjectController.extend();

module.exports = controller;

},{}],5:[function(require,module,exports){
var controller = Ember.Controller.extend({
  needs: ['application']
});

module.exports = controller;

},{}],6:[function(require,module,exports){

App.ApplicationController = require("./application");
App.NavigationController = require("./navigation");
App.TaskController = require("./task");
App.TasksController = require("./tasks");
App.CompletedController = require("./completed");
App.CompletedTaskController = require("./completedTask");
App.ConfigureController = require("./configure");

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

},{"./application":2,"./completed":3,"./completedTask":4,"./configure":5,"./navigation":7,"./task":8,"./tasks":9}],7:[function(require,module,exports){
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

},{}],8:[function(require,module,exports){
var controller = Ember.ObjectController.extend({
  actions: {
    'complete': function(){
      var url = this.store.adapterFor('task').buildURL('task', this.get('uuid')) + 'complete/';
      var self = this;
      $.ajax({
        url: url,
        dataType: 'json',
        statusCode: {
          200: function(){
            self.get('model').unloadRecord();
            self.transitionToRoute('tasks');
          },
        }
      });
    },
    'delete': function(){
      var url = this.store.adapterFor('task').buildURL('task', this.get('uuid')) + 'delete/';
      $.ajax({
        url: url,
        dataType: 'json',
        statusCode: {
          200: function(){
            self.get('model').unloadRecord();
            self.transitionToRoute('tasks');
          },
          501: function(){
            alert("Deleting tasks is currently unimplemented");
          }
        }
      });
    }
  }
});

module.exports = controller;

},{}],9:[function(require,module,exports){
var controller = Ember.ArrayController.extend({
  sortProperties: ['urgency'],
  sortAscending: false,

  actions: {
    view_task: function(task){
      this.transitionToRoute('task', task);
    }
  }
});

module.exports = controller;

},{}],10:[function(require,module,exports){

Ember.Handlebars.registerHelper('comma_to_list', function(item, options){
  return item.split(',')
});

},{}],11:[function(require,module,exports){
window.App = require('./app');

require("./controllers");
require("./models");
require("./routes");
require("./views");
require("./helpers");

},{"./app":1,"./controllers":6,"./helpers":10,"./models":12,"./routes":18,"./views":23}],12:[function(require,module,exports){

App.User = require("./user.js");
App.Task = require("./task.js");

},{"./task.js":13,"./user.js":14}],13:[function(require,module,exports){
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
  uuid: DS.attr('string'),
  depends: DS.attr('string'),

  editable: function(){
    if (this.get('status') == 'pending') {
      return true;
    }
    return false;
  }.property('status'),

  icon: function(){
    if (this.get('status') == 'completed') {
      return 'fa-check-square-o';
    } else {
      return 'fa-square-o';
    }
  }.property('status', 'urgency'),

  dependent_tickets: function(){
    var value = this.get('depends');
    var values = [];
    if (value) {
      var ticket_ids = value.split(',');
      for(var i = 0; i < ticket_ids.length; i++) {
        values[values.length] = this.store.find('task', ticket_ids[i]);
      }
      return values;
    } else {
      return [];
    }
  }.property('depends')
});

module.exports = model;

},{}],14:[function(require,module,exports){
var model = DS.Model.extend({
  logged_in: DS.attr('boolean'),
  uid: DS.attr('string'),
  username: DS.attr('string'),
  name: DS.attr('string'),
  email: DS.attr('string'),
  configured: DS.attr('boolean'),
  taskd_credentials: DS.attr('string'),
  taskd_server: DS.attr('string'),
  api_key: DS.attr('string')
});

module.exports = model;

},{}],15:[function(require,module,exports){
App.Router.map(function(){
  this.route("login", {path: "/login"});
  this.route("about", {path: "/about"});
  this.resource("tasks", function(){
    this.resource("task", {path: "/:uuid"});
  });
  this.resource("completed", function(){
    this.resource("completedTask", {path: "/:uuid"});
  });
  this.route("unconfigurable", {path: "/no-tasks"});
  this.route("configure", {path: "/configure"});
  this.route("getting_started", {path: "/getting-started"});
});

App.Router.reopen({
  location: 'history'
});

},{}],16:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(){
    return this.store.findQuery('task', {completed: 1, order_by: '-modified'});
  }
});

module.exports = route;

},{}],17:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(params) {
    return this.store.find('task', params.uuid);
  }
});

module.exports = route;

},{}],18:[function(require,module,exports){

App.IndexRoute = Ember.Route.extend({
  renderTemplate: function() {
    this.render('index');
    this.render('navigation', {outlet: 'navigation'});
  }
});
App.TasksRoute = require("./tasks");
App.TaskRoute = require("./task");
App.CompletedRoute = require("./completed");
App.CompletedTaskRoute = require("./completedTask");

},{"./completed":16,"./completedTask":17,"./task":19,"./tasks":20}],19:[function(require,module,exports){
module.exports=require(17)
},{}],20:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(){
    return this.store.findQuery('task', {completed: 0});
  },
  beforeModel: function() {
    this.store.unloadAll(App.Task);
  },
  afterModel: function(tasks, transition) {
    if (tasks.get('length') === 0) {
      this.transitionTo('getting_started');
    }
  }
});

module.exports = route;

},{}],21:[function(require,module,exports){
var view = Ember.View.extend({
  templateName: 'tasks',
  name: 'completed'
});

module.exports = view;

},{}],22:[function(require,module,exports){
var view = Ember.View.extend({
  templateName: 'task',
  name: 'completedTask'
});

module.exports = view;

},{}],23:[function(require,module,exports){

App.NavigationView = require("./navigation");
App.CompletedView = require("./completed");
App.CompletedTaskView = require("./completedTask");

},{"./completed":21,"./completedTask":22,"./navigation":24}],24:[function(require,module,exports){
var view = Ember.View.extend();

module.exports = view;

},{}]},{},[1,10,11,15])