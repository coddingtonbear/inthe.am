var route = Ember.Route.extend({
  model: function(){
    // Manually enumerate over loaded records; only try to
    // unload records that are marked as loaded -- otherwise, may
    // throw "attempted to handle event 'unloadRecord' while in state
    // root.empty.
    var all = this.store.all(App.Task);
    for (var i = 0; i < all.content.length; i++) {
      var record = all.content[i];
      if (record.get('isLoaded')) {
        this.store.unloadRecord(record);
      }
    }
    return this.store.findQuery('task', {'status': 'pending'});
  },
  afterModel: function(tasks, transition) {
    if (tasks.get('length') === 0) {
      this.transitionTo('getting_started');
    } else if (transition.targetName == "tasks.index") {
      this.transitionTo('task', tasks.get('firstObject'));
    }
  }
});

module.exports = route;
