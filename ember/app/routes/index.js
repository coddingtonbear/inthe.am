import Ember from 'ember'

var route = Ember.Route.extend({
  renderTemplate: function () {
    this.render('index')
  }
})

export default route
