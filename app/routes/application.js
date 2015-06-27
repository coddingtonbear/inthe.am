import Ember from "ember";

var route = Ember.Route.extend({
    actions: {
        disconnectModalOutlet: function(){
            this.disconnectOutlet({
                parentView: 'application',
                outlet: 'modal'
            });
        },
        edit_task: function(task) {
            task = task ? task : this.controllerFor('task').get('model');
            this.controllerFor('create-task-modal').set('model', task);
            var rendered = this.render(
                'create-task-modal',
                {
                    'into': 'application',
                    'outlet': 'modal',
                }
            );
            Ember.run.next(null, function(){
                $(document).foundation();
                $("#new_task_form").foundation('reveal', 'open');
                setTimeout(function(){$("input[name=description]").focus();}, 500);
            });
            return rendered;
        },
        create_task: function() {
            var record = null;
            record = this.store.createRecord('task', {});
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
