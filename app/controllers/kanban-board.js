import Ember from "ember";

var KANBAN_ID_URL_RE = window.RegExp(".*kanban/([a-f0-9-]{36})");

var controller = Ember.ObjectController.extend({
    needs: ['application'],
    title: function(){
        var matched = KANBAN_ID_URL_RE.exec(window.location.href);
        if (matched) {
            var id = matched[1];
            var memberships = this.get('controllers.application').user.kanban_memberships;
            var reduced = memberships.reduce(function(prev, curr){
                if(curr[1].indexOf(id) > -1) {
                    return curr;
                } else {
                    return prev;
                }
            });
            return reduced[0];
        } else {
            return "Untitled Kanban Board";
        }
    }.property('model'),
    tasks: function(){
        return this.store.find('kanban-task');
    }.property('model'),
});

export default controller;
