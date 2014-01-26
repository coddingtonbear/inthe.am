var view = Ember.View.extend({
  didInsertElement: function(){
    this.controller.transitionTo('tasks');
  }
});

module.exports = view;
