var route = Ember.Route.extend({
  beforeModel: function(transition) {
    // Manually enumerate over loaded records; only try to
    // unload records that are marked as loaded -- otherwise, may
    // throw "attempted to handle event 'unloadRecord' while in state
    // root.empty.
    var all = this.store.all(App.Task);
    for (var i = 0; i < all.content.length; i++) {
      var record = all.content[i];
      if (record.get('isLoaded') && !record.get('isDirty')) {
        this.store.unloadRecord(record);
      }
    }
  }
});

module.exports = route;
