import Ember from "ember";

var route = Ember.Route.extend({
    model: function() {
        var application = this.controllerFor('application');
        application.showLoading();
        return this.store.find('activity-log').then(function(data){
            application.hideLoading();
            return data;
        });
    }
});

export default route;
