import Ember from 'ember'
import config from './config/environment'

var Router = Ember.Router.extend({
  location: config.locationType,
  rootURL: config.rootURL
})

Router.map(function () {
  this.route('login', {path: '/login'})
  this.route('about', {path: '/about'})
  this.resource('add-to-home-screen', {path: '/add-to-home-screen'})
  this.resource('mobile-tasks', {path: '/mobile-tasks'})
  this.route('create-task', {path: '/create-task'})
  this.route('edit-task', {path: '/edit-task/:uuid'})
  this.resource('tasks', function () {
    this.resource('task', {path: '/:uuid'})
  })
  this.resource('activity-log', {path: '/activity-log'})
  this.route('configure', {path: '/configure'})
  this.route('getting-started', {path: '/getting-started'})
  this.route('terms-of-service', {path: '/terms-of-service'})
  this.route('four-oh-four', {path: '*path'})
})

export default Router
