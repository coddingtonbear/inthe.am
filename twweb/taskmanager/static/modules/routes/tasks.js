var route = Ember.Route.extend({
  model: function(){
    return this.store.find('task');
  }
});

module.exports = route;
