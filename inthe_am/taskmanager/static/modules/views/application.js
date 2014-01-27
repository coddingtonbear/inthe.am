var view = Ember.View.extend({
  didInsertElement: function(){
    $(document).foundation();
  }
});

module.exports = view;
