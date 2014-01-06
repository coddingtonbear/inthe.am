var route = Ember.Route.extend({
  model: function(params) {
    return this.store.find('task', params.uuid);
  }
});

module.exports = route;
