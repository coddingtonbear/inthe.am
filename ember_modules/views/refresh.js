var view = Ember.View.extend({
  didInsertElement: function(){
    this.controller.transitionToRoute('tasks');
  }
});

module.exports = view;
