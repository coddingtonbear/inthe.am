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

},{"./application":2,"./navigation":4}],4:[function(require,module,exports){
var controller = Ember.Controller.extend({
  needs: "application"
});

module.exports = controller;

},{}],5:[function(require,module,exports){

},{}],6:[function(require,module,exports){
window.App = require('./app');

require("./controllers");
require("./models");
require("./routes");
require("./views");
require("./helpers");

},{"./app":1,"./controllers":3,"./helpers":5,"./models":7,"./routes":10,"./views":11}],7:[function(require,module,exports){

App.User = require("./user.js");

},{"./user.js":8}],8:[function(require,module,exports){
var model = DS.Model.extend({
  logged_in: DS.attr('boolean'),
  uid: DS.attr('string'),
  email: DS.attr('string'),
  dropbox_configured: DS.attr('boolean'),
});

module.Exports = model;

},{}],9:[function(require,module,exports){
App.Router.map(function(){
  this.route("login", {path: "/login"});
});

},{}],10:[function(require,module,exports){

App.IndexRoute = Ember.Route.extend({
  renderTemplate: function() {
    this.render('index');
    this.render('navigation', {outlet: 'navigation'});
  }
});

},{}],11:[function(require,module,exports){

App.NavigationView = require("./navigation");

},{"./navigation":12}],12:[function(require,module,exports){
var view = Ember.View.extend();

module.exports = view;

},{}]},{},[1,5,6,9])