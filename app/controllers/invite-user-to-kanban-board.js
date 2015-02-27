import Ember from "ember";

var controller = Ember.ObjectController.extend({
    needs: ['application', 'kanban-board'],
    roleOptions: [
        {value: "member", name: "Member"},
        {value: "owner", name: "Owner"},
    ],
    ajaxRequest: function(params) {
        return this.get('controllers.application').ajaxRequest(params);
    },
    error_message: function(message) {
        this.get('controllers.application').error_message(message);
    },
    success_message: function(message) {
        this.get('controllers.application').success_message(message);
    },
    actions: {
        invite: function() {
            var application = this.get('controllers.application');
            var url = this.get('controllers.kanban-board').getBoardUrl(
                "members/invite/"
            );
            var email = (
                $("form#invite_user_form input[name='email_address']").val()
            );
            var role = (
                $("form#invite_user_form select[name='role']").val()
            );
            application.showLoading();
            this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {
                    email: email,
                    role: role,
                }
            }).then(function(){
                application.hideLoading();
                this.success_message(
                    `An invitation email has been sent to ${email}.`
                );
                application.closeModal($('#invite_user_form'));
                $("form#invite_user_form input[name='email_address']").val('');
            }.bind(this), function(msg){
                application.hideLoading();
                this.error_message(
                    `An error was encountered while attempting to ` +
                    `invite ${email}: ${msg}`
                );
            }.bind(this));
        }
    }
});

export default controller;
