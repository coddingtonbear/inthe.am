import Ember from "ember";

var route = Ember.Route.extend({
    renderTemplate: function(_, error){
        this._super();
        var self = this;
    },
});

export default route;
