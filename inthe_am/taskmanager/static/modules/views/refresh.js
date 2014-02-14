var view = Ember.View.extend({
  didInsertElement: function(){
    this._super();
    this.controller.transitionToRoute('tasks');
  }
});

module.exports = view;
