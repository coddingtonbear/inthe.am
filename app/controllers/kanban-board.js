import Ember from "ember";

var KANBAN_ID_URL_RE = window.RegExp(".*kanban/([a-f0-9-]{36})");

var controller = Ember.ObjectController.extend({
    needs: ['application'],
    ajaxRequest: function(params) {
        return this.get('controllers.application').ajaxRequest(params);
    },
    getBoardId: function(){
        var matched = KANBAN_ID_URL_RE.exec(window.location.href);
        if (matched) {
            return matched[1];
        }
    },
    getBoardUrl: function(){
        return '/api/v1/kanban/' + this.getBoardId() + '/meta/';
    },
    meta: function(){
        return this.store.find('kanban-board', this.getBoardId());
    }.property('model'),
    tasks: function(){
        return this.store.find('kanban-task');
    }.property('model'),
});

export default controller;
