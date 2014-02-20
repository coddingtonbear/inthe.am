var route = Ember.Route.extend({
  renderTemplate: function(_, error){
    this._super();
    var self = this;
    Ember.run.once(_, function(){
      reportError(error);
      Ember.run.next(_, function(){
        setTimeout(3000, window.location.reload);
      });
    });
  },
});

module.exports = route;
