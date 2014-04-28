var controller = Ember.Controller.extend({
  needs: ['application', 'configure'],
  actions: {
    enable_pebble_cards: function() {
      this.get('controllers.configure').send('save_pebble_cards', 1);
    },
    enable_feed: function() {
      this.get('controllers.configure').send('save_feed', 0);
    }
  }
});

module.exports = controller;
