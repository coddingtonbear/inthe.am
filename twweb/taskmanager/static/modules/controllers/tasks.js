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
