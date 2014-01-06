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
