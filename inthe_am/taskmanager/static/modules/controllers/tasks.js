var controller = Ember.ArrayController.extend({
  sortProperties: ['urgency'],
  sortAscending: false,
  refresh: function(){
    this.get('content').update();
  },
  pendingTasks: function() {
    return this.get('model').filterProperty('status', 'pending');
  }.property('model.@each.status')
});

module.exports = controller;
