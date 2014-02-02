var view = Ember.View.extend({
  initializeFoundation: function(){
    Ember.run.next(
      this,
      function(){
        Ember.$(document).foundation();
      }
    );
  },
  didInsertElement: function(){
    setInterval(
      this.initializeFoundation,
      1000
    );
  }
});

module.exports = view;
