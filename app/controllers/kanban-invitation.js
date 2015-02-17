import Ember from "ember";

var controller = Ember.ObjectController.extend({
    needs: ['application', 'kanban-board'],
    ajaxRequest: function(params) {
        return this.get('controllers.application').ajaxRequest(params);
    },
    error_message: function(message) {
        this.get('controllers.application').error_message(message);
    },
    success_message: function(message) {
        this.get('controllers.application').success_message(message);
    },
    respondToInvitation: function(accept=true) {
        var application = this.get('controllers.application');
        var url = this.get('controllers.kanban-board').getBoardUrl(
            "members/respond/"
        );
        application.showLoading();
        this.ajaxRequest({
            url: url,
            method: 'POST',
            data: {
                accepted: accept ? 1 : 0,
                uuid: this.model.uuid
            }
        }).then(function(){
            application.hideLoading();
            this.success_message(
                `You are now a member of the "${this.model.board.name}" ` +
                `Team Kanban Board.`
            );
            this.transitionToRoute(
                'kanban-board',
                this.get('model.board.uuid')
            );
            setTimeout(function(){
                window.location.reload();
            }, 3000);
        }.bind(this), function(msg){
            application.hideLoading();
            this.error_message(
                `An error was encountered while attempting to ` +
                `accept your membership: ${msg}`
            );
        }.bind(this));
    },
    actions: {
        accept: function() {
            this.respondToInvitation(true);
        },
        reject: function() {
            this.respondToInvitation(false);
        }
    }
});

export default controller;
