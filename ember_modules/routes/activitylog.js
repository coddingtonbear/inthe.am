var route = Ember.Route.extend({
  model: function() {
    var application = this.controllerFor('application');
    application.showLoading();
    return this.store.find('activitylog').then(function(data){
      application.hideLoading();
      return data;
    });
  }
});

module.exports = route;
