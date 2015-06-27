import Ember from "ember";

var controller = Ember.ObjectController.extend({
    needs: ['application', 'tasks'],
    priorities: [
        {short: '', long: '(none)'},
        {short: 'L', long: 'Low'},
        {short: 'M', long: 'Medium'},
        {short: 'H', long: 'High'},
    ],
    actions: {
        'save': function() {
            var model = this.get('model');
            var application = this.get('controllers.application');
            var self = this;
            application.showLoading();
            model.save().then(function(){
                application.closeModal($('#new_task_form'));
                application.hideLoading();
                self.transitionToRoute('task', model);
            }.bind(this), function(reason){
                model.rollback();
                model.reload();
                application.hideLoading();
                application.error_message(
                    "An error was encountered while " +
                    "saving this task.  Check your " +
                    "Activity Log for more information."
                );
                application.get('handleError').bind(application)(reason);
            }.bind(this));
        }
    }
});

export default controller;
