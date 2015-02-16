import Ember from "ember";

var KANBAN_ID_URL_RE = window.RegExp(".*kanban/([a-f0-9-]{36})");

var controller = Ember.ObjectController.extend({
    needs: ['application'],
    ASSIGNEE: 'intheamkanbanassignee',
    getBoardId: function(){
        var matched = KANBAN_ID_URL_RE.exec(window.location.href);
        if (matched) {
            return matched[1];
        }
    },
    getBoardUrl: function(post="meta/"){
        return '/api/v1/kanban/' + this.getBoardId() + '/' + post;
    },
    meta: function(){
        return this.store.find('kanban-board', this.getBoardId());
    }.property('model'),
    tasks: function() {
        return this.store.find('kanban-task');
    }.property('model'),
    columns: function(){
        if(! this.get('model')) {
            return [];
        }

        var columns = [{name: 'Backlog'}];
        this.get('meta').then(function(metadata) {
            metadata.get('columns').forEach(
                function(col) {
                    columns.pushObject(col);
                }.bind(this)
            );
        });
        return columns;
    }.property('model'),
    actions: {
        assign_to_me: function(task) {
            var email = this.get('controllers.application.user').email;
            if(task.get(this.ASSIGNEE) !== email) {
                task.set(
                    this.ASSIGNEE,
                    this.get('controllers.application.user').email
                );
            } else {
                task.set(this.ASSIGNEE, '');
            }
            task.save();
        }
    }
});

export default controller;
