import Ember from 'ember'

var view = Ember.View.extend({
  taskObserver: function () {
    $('#task-details').scrollTop(0)
  }.observes('controller.model')
})

export default view
