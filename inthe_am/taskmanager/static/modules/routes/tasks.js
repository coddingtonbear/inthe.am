var route = Ember.Route.extend({
  model: function(){
    return this.store.findQuery('task', {completed: 0});
  }
});

module.exports = route;
