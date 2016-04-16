import Ember from "ember";

var route = Ember.Route.extend({
    actions: {
        edit_task: function(task) {
            console.logIfDebug("Showing edit task modal...");
            this.render(
                'create-task-modal',
                {
                    'into': 'application',
                    'outlet': 'modal',
                    'model': (
                        task ? task : this.controllerFor('task').get('model')
                    )
                }
            );
            Ember.run.next(null, function(){
                $(document).foundation();
                $("#new_task_form").foundation('reveal', 'open');
                setTimeout(function(){$("input[name=description]").focus();}, 500);
            });
        },
        create_task: function() {
            this.render(
                'create-task-modal',
                {
                    'into': 'application',
                    'outlet': 'modal',
                    'model': this.store.createRecord('task', {})
                }
            );
            Ember.run.next(null, function(){
                $(document).foundation();
                $("#new_task_form").foundation('reveal', 'open');
                setTimeout(function(){$("input[name=description]").focus();}, 500);
            });
        }
    }
});

export default route;
