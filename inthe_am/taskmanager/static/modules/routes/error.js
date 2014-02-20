var route = Ember.Route.extend({
  renderTemplate: function(_, error){
    this._super();
    var self = this;
    Ember.run.once(_, function(){
      reportError(error);
    });
  },
});

module.exports = route;
