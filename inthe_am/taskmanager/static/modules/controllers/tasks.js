var controller = Ember.ArrayController.extend({
  sortProperties: ['urgency'],
  sortAscending: false,
  refresh: function(){
    console.log("Updating tasks...");
    this.get('content').update();
  }
});

module.exports = controller;
