var route = Ember.Route.extend({
  renderTemplate: function(_, error){
    this._super();
    var self = this;
    setTimeout(function(){
      self.controllerFor('application').reportError(error);
      var url = self.controllerFor('application').urls.about;
      window.location = url;
    }, 3000);
  },
});

module.exports = route;
