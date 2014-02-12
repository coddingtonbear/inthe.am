var route = Ember.Route.extend({
  renderTemplate: function(_, error){
    this._super();
    var self = this;
    Ember.run.once(_, function(){
      reportError(error);
      Ember.run.next(_, function(){
        var url = self.controllerFor('application').urls.about;
        window.location = url;
      });
    });
  },
});

module.exports = route;
