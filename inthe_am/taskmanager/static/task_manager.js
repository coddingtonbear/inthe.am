(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);throw new Error("Cannot find module '"+o+"'")}var f=n[o]={exports:{}};t[o][0].call(f.exports,function(e){var n=t[o][1][e];return s(n?n:e)},f,f.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
var App = Ember.Application.create({
  LOG_TRANSITIONS: true
});

App.ApplicationAdapter = DS.DjangoTastypieAdapter.extend({
  namespace: 'api/v1'
});
App.ApplicationSerializer = DS.DjangoTastypieSerializer.extend();

module.exports = App;

},{}],2:[function(require,module,exports){
var controller = Ember.Controller.extend({
  needs: ['application']
});

module.exports = controller;

},{}],3:[function(require,module,exports){
var controller = Ember.Controller.extend({
  user: null,
  pending_count: null,
  csrftoken: null,
  urls: {
    logout: '/logout/',
    login: '/login/google-oauth2/',
    ca_certificate: '/api/v1/user/ca-certificate/',
    my_certificate: '/api/v1/user/my-certificate/',
    my_key: '/api/v1/user/my-key/',
    taskrc_extras: '/api/v1/user/taskrc/',
    sms_url: null,
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
    this.set('urls.sms_url', this.get('user').sms_url);
  },
  getCookie: function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});

module.exports = controller;

},{}],4:[function(require,module,exports){
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

},{}],5:[function(require,module,exports){
var controller = Ember.ObjectController.extend();

module.exports = controller;

},{}],6:[function(require,module,exports){
var controller = Ember.Controller.extend({
  needs: ['application'],

  actions: {
    save_taskrc: function() {
      var csrftoken = this.get('controllers.application').getCookie(
        'csrftoken'
      );
      var url = this.get('controllers.application').urls.taskrc_extras;
      var value = $('textarea[name=custom_taskrc]').val();

      $.ajax({
        url: url,
        type: 'PUT',
        headers: {
          'X-CSRFToken': csrftoken
        },
        dataType: 'text',
        data: value
      });
    }
  }
});

module.exports = controller;

},{}],7:[function(require,module,exports){

App.ApplicationController = require("./application");
App.NavigationController = require("./navigation");
App.TaskController = require("./task");
App.TasksController = require("./tasks");
App.CompletedController = require("./completed");
App.CompletedTaskController = require("./completedTask");
App.ApiAccessController = require("./api_access");
App.SynchronizationController = require("./synchronization");
App.ConfigureController = require("./configure");
App.SmsController = require("./sms");

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

},{"./api_access":2,"./application":3,"./completed":4,"./completedTask":5,"./configure":6,"./navigation":8,"./sms":9,"./synchronization":10,"./task":11,"./tasks":12}],8:[function(require,module,exports){
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

},{}],9:[function(require,module,exports){
module.exports=require(2)
},{}],10:[function(require,module,exports){
module.exports=require(2)
},{}],11:[function(require,module,exports){
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
            self.transitionToRoute('refresh');
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
            self.transitionToRoute('refresh');
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

},{}],12:[function(require,module,exports){
var controller = Ember.ArrayController.extend({
  sortProperties: ['urgency'],
  sortAscending: false,
});

module.exports = controller;

},{}],13:[function(require,module,exports){

Ember.Handlebars.helper('comma_to_list', function(item, options){
  return item.split(',');
});

Ember.Handlebars.helper('propercase', function(project_name, options) {
  if (project_name) {
    var properCase = function(txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    };
    return project_name.replace('_', ' ').replace(/\w\S*/g, properCase);
  }
});

Ember.Handlebars.helper('calendar', function(date, options) {
  if (date) {
    return new Handlebars.SafeString('<span class="calendar date" title="' + moment(date).format('LLLL') + '">' + moment(date).calendar() + "</span>");
  }
});

},{}],14:[function(require,module,exports){
window.App = require('./app');

require("./controllers");
require("./models");
require("./routes");
require("./views");
require("./helpers");

},{"./app":1,"./controllers":7,"./helpers":13,"./models":15,"./routes":21,"./views":27}],15:[function(require,module,exports){

App.User = require("./user.js");
App.Task = require("./task.js");

App.DirectTransform = DS.Transform.extend({
  serialize: function(value) {
    return value;
  },
  deserialize: function(value) {
    return value;
  }
});

},{"./task.js":16,"./user.js":17}],16:[function(require,module,exports){
var model = DS.Model.extend({
  annotations: DS.attr(),
  tags: DS.attr(),
  description: DS.attr('string'),
  due: DS.attr('date'),
  entry: DS.attr('date'),
  modified: DS.attr('date'),
  priority: DS.attr('string'),
  resource_uri: DS.attr('string'),
  start: DS.attr('date'),
  wait: DS.attr('date'),
  scheduled: DS.attr('date'),
  'status': DS.attr('string'),
  urgency: DS.attr('number'),
  uuid: DS.attr('string'),
  depends: DS.attr('string'),
  project: DS.attr('string'),
  imask: DS.attr('number'),

  editable: function(){
    if (this.get('status') == 'pending') {
      return true;
    }
    return false;
  }.property('status'),

  icon: function() {
    if (this.get('status') == 'completed') {
      return 'fa-check-circle-o';
    } else if (this.get('start')) {
      return 'fa-asterisk';
    } else if (this.get('due')) {
      return 'fa-clock-o';
    } else {
      return 'fa-circle-o';
    }
  }.property('status', 'start', 'due'),

  taskwarrior_class: function() {
    if (this.get('start')) {
      return 'active';
    } else if (moment(this.get('due')).isBefore(moment())) {
      return 'overdue';
    } else if (moment().startOf('day').isBefore(this.get('due')) && moment().endOf('day').add('s', 2).isAfter(this.get('due'))) {
      return 'due__today';
    } else if (this.get('imask')) {
      return 'recurring';
    } else if (this.get('due')) {
      return 'due';
    } else if (this.get('priority') == 'H') {
      return 'pri__H';
    } else if (this.get('priority') == 'M') {
      return 'pri__M';
    } else if (this.get('priority') == 'L') {
      return 'pri__L';
    } else if (this.get('tags')) {
      return 'tagged';
    }
  }.property('status', 'urgency', 'start', 'due'),

  processed_annotations: function() {
    var value = this.get('annotations');
    if (value) {
      for (var i = 0; i < value.length; i++) {
        value[i] = {
          entry: new Date(Ember.Date.parse(value[i].entry)),
          description: value[i].description
        };
      }
    } else {
      return [];
    }
    return value;
  }.property('annotations'),

  dependent_tickets: function(){
    var value = this.get('depends');
    var values = [];
    if (value) {
      var ticket_ids = value.split(',');
      var add_value_to_values = function(value) {
        values[values.length] = value;
      };
      for (var i = 0; i < ticket_ids.length; i++) {
        this.store.find('task', ticket_ids[i]).then(add_value_to_values);
      }
      return values;
    } else {
      return [];
    }
  }.property('depends'),

  as_json: function() {
    return JSON.stringify(this.store.serialize(this));
  }.property()
});

module.exports = model;

},{}],17:[function(require,module,exports){
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

},{}],18:[function(require,module,exports){
App.Router.map(function(){
  this.route("login", {path: "/login"});
  this.route("about", {path: "/about"});
  this.route("refresh", {path: "/refresh"});
  this.resource("tasks", function(){
    this.resource("task", {path: "/:uuid"});
  });
  this.resource("completed", function(){
    this.resource("completedTask", {path: "/:uuid"});
  });
  this.route("unconfigurable", {path: "/no-tasks"});
  this.route("api_access", {path: "/api-access"});
  this.route("synchronization", {path: "/synchronization"});
  this.route("configure", {path: "/configure"});
  this.route("getting_started", {path: "/getting-started"});
  this.route("sms", {path: "/sms"});
});

App.Router.reopen({
  location: 'history'
});

},{}],19:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(){
    return this.store.findQuery('task', {completed: 1, order_by: '-modified'});
  }
});

module.exports = route;

},{}],20:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(params) {
    return this.store.find('task', params.uuid);
  }
});

module.exports = route;

},{}],21:[function(require,module,exports){

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
App.RefreshRoute = require("./refresh");

},{"./completed":19,"./completedTask":20,"./refresh":22,"./task":23,"./tasks":24}],22:[function(require,module,exports){
var route = Ember.Route.extend({
  beforeModel: function(transition) {
    // Manually enumerate over loaded records; only try to
    // unload records that are marked as loaded -- otherwise, may
    // throw "attempted to handle event 'unloadRecord' while in state
    // root.empty.
    var all = this.store.all(App.Task);
    for (var i = 0; i < all.content.length; i++) {
      var record = all.content[i];
      if (record.get('isLoaded')) {
        this.store.unloadRecord(record);
      }
    }
  }
});

module.exports = route;

},{}],23:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(params) {
     return this.store.find('task', params.uuid);
  }
});

module.exports = route;

},{}],24:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(){
    return this.store.findQuery('task', {'status': 'pending'});
  },
  afterModel: function(tasks, transition) {
    if (tasks.get('length') === 0) {
      this.transitionTo('getting_started');
    } else if (transition.targetName == "tasks.index") {
      this.transitionTo('task', tasks.get('firstObject'));
    }
  }
});

module.exports = route;

},{}],25:[function(require,module,exports){
var view = Ember.View.extend({
  templateName: 'tasks',
  name: 'completed'
});

module.exports = view;

},{}],26:[function(require,module,exports){
var view = Ember.View.extend({
  templateName: 'task',
  name: 'completedTask'
});

module.exports = view;

},{}],27:[function(require,module,exports){

App.NavigationView = require("./navigation");
App.CompletedView = require("./completed");
App.CompletedTaskView = require("./completedTask");
App.RefreshView = require("./refresh");

},{"./completed":25,"./completedTask":26,"./navigation":28,"./refresh":29}],28:[function(require,module,exports){
var view = Ember.View.extend();

module.exports = view;

},{}],29:[function(require,module,exports){
var view = Ember.View.extend({
  didInsertElement: function(){
    this.controller.transitionTo('tasks');
  }
});

module.exports = view;

},{}]},{},[1,13,14,18])