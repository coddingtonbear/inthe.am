import Ember from "ember";

var route = Ember.Route.extend({
    model: function(){
        return this.store.findQuery('task', {completed: 1, order_by: '-modified'});
    }
});

export default route;
