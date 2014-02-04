var controller = Ember.ArrayController.extend({
  sortProperties: ['urgency'],
  sortAscending: false,
  refresh: function(){
    this.get('content').update();
  }
});

module.exports = controller;
