var controller = Ember.ArrayController.extend({
  sortProperties: ['urgency'],
  sortAscending: false,

  actions: {
    view_task: function(task){
      this.transitionToRoute('task', task);
    }
  },
});

module.exports = controller;
