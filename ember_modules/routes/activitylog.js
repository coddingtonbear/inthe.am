var route = Ember.Route.extend({
  model: function() {
    return this.store.find('activitylog');
  }
});

module.exports = route;
