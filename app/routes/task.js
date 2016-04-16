import Ember from "ember";

var route = Ember.Route.extend({
    model: function(params) {
        var application = this.controllerFor('application');
        if(!this.store.hasRecordForId('task', params.uuid)) {
            application.showLoading();
        }
        return this.store.findRecord('task', params.uuid);
    },
    afterModel: function() {
        var application = this.controllerFor('application');
        application.hideLoading();
    },
    actions: {
        edit: function(){
            if (this.controllerFor('application').isSmallScreen()) {
                this.transitionTo('edit-task', this.controllerFor('task').get('model'));
            } else {
                var rendered = this.render(
                    'create-task-modal',
                    {
                        'into': 'application',
                        'outlet': 'modal',
                        'model': this.controllerFor('task').get('model')
                    }
                );
                Ember.run.next(null, function(){
                    $(document).foundation();
                    $("#new_task_form").foundation('reveal', 'open');
                    setTimeout(function(){$("input[name=description]").focus();}, 500);
                });
                return rendered;
            }
        },
        add_annotation: function(){
            this.render(
                'create_annotation',
                {
                    'into': 'application',
                    'outlet': 'modal',
                    'model': this.controllerFor('task').get('model')
                }
            );
            Ember.run.next(null, function(){
                $(document).foundation();
                $("#new_annotation_form").foundation('reveal', 'open');
                setTimeout(function(){$("#new_annotation_body").focus();}, 500);
            });
        },
        error: function(reason, tsn) {
            var application = this.controllerFor('application');
            application.get('handleError').bind(application)(reason, tsn);
        },
    }
});

export default route;
