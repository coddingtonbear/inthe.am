var controller = Ember.ArrayController.extend({
  refresh: function(){
    try {
      this.get('content').update();
    } catch (e) {
      // Nothing to worry about -- probably just not loaded.
    }
  },
});

module.exports = controller;
