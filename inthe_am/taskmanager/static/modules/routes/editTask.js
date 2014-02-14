var route = Ember.Route.extend({
  setupController: function(controller, model) {
    controller.set('model', model);
  }
});

module.exports = route;
