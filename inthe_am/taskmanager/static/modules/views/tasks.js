var view = Ember.View.extend({
  didInsertElement: function(){
    $('body > .ember-view').offset({top: 0});
  }
});

module.exports = view;
