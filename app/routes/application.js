import Ember from "ember";

var KANBAN_ID_RE = window.RegExp("/api/v1/kanban/([^/]+)/members/([^/]+)");

var route = Ember.Route.extend({
    getKanbanBoardIdFromMembership: function(membershipUrl){
        var matched = KANBAN_ID_RE.exec(membershipUrl);
        if (matched) {
            return matched[1];
        } else {
            return null;
        }
    },
    actions: {
        'switch_to_kanban': function(){
            var memberships = this.controllerFor('application').user.kanban_memberships;
            if (memberships.length === 1) {
                var kanbanBoardId = this.getKanbanBoardIdFromMembership(memberships[0][1]);
                // Unfortunately, we must set this global because we will
                // need to use it for building the KanbanTask item URLs.
                if (!kanbanBoardId) {
                    console.log(
                        "Error: could not identify Kanban Board ID from membership URL",
                        memberships[0][1]
                    );
                }
                Ember.KANBAN_BOARD_ID = kanbanBoardId;
                this.store.unloadAll('kanban-task');
                this.transitionTo('kanban-board', {uuid: kanbanBoardId});
            } else {
                console.log("Error; either zero or more than one kanban board membership.");
            }
        },
        'create_task': function() {
            var currentPath = this.controllerFor('application').getHandlerPath();
            var record = null;
            if (currentPath === 'application.kanban-board') {
                record = this.store.createRecord('kanban-task', {});
            } else {
                record = this.store.createRecord('task', {});
            }
            this.controllerFor('create-task-modal').set('model', record);

            var rendered = this.render(
                'create-task-modal',
                {
                    'into': 'application',
                    'outlet': 'modal',
                }
            );
            var displayModal = function(){
                $(document).foundation();
                $("#new_task_form").foundation('reveal', 'open');
                setTimeout(function(){$("input[name=description]").focus();}, 500);
            };
            Ember.run.scheduleOnce('afterRender', this, displayModal);
            return rendered;
        }
    }
});

export default route;
