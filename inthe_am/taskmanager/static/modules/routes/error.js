var route = Ember.Route.extend({
  renderTemplate: function(_, error){
    this._super();
    var self = this;
    Ember.run.next(self, function(){
      self.controllerFor('application').reportError(error);
      var url = self.controllerFor('application').urls.about;
      window.location = url;
    });
  },
});

module.exports = route;
