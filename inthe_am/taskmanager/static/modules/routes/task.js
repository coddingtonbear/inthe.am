var route = Ember.Route.extend({
  model: function(params) {
     this.store.find('task', params.uuid);
  },
});

module.exports = route;
