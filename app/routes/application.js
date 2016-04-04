import Ember from "ember";

var route = Ember.Route.extend({
    actions: {
        edit_task: function(task) {
            console.logIfDebug("Showing edit task modal...")
            this.render(
                'create-task-modal',
                {
                    'into': 'application',
                    'outlet': 'modal',
                }
            );
            task = task ? task : this.controllerFor('task').get('model');
            this.controllerFor('create-task-modal').set('model', task);
            Ember.run.next(null, function(){
                $(document).foundation();
                $("#new_task_form").foundation('reveal', 'open');
                setTimeout(function(){$("input[name=description]").focus();}, 500);
            });
        },
        create_task: function() {
            console.logIfDebug("Showing create task modal...")
            this.render(
                'create-task-modal',
                {
                    'into': 'application',
                    'outlet': 'modal',
                }
            );
            var record = this.store.createRecord('task', {});
            this.controllerFor('create-task-modal').set('model', record);
            Ember.run.next(null, function(){
                $(document).foundation();
                $("#new_task_form").foundation('reveal', 'open');
                setTimeout(function(){$("input[name=description]").focus();}, 500);
            });
        }
    }
});

export default route;
