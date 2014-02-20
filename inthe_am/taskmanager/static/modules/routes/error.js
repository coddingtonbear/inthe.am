var route = Ember.Route.extend({
  renderTemplate: function(_, error){
    this._super();
    var self = this;
    Ember.run.once(_, function(){
      reportError(error);
      Ember.run.next(_, function(){
        setTimeout(function(){window.location.reload();}, 10000);
      });
    });
  },
});

module.exports = route;
