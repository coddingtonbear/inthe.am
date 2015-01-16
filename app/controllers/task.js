import Ember from "ember";

var controller = Ember.ObjectController.extend({
    needs: ['application', 'tasks'],
    actions: {
        'complete': function(){
            var result = confirm("Are you sure you would like to mark this task as completed?");
            if(result) {
                var self = this;
                this.get('controllers.application').showLoading();
                this.get('model').destroyRecord().then(function(){
                    self.get('controllers.application').hideLoading();
                    self.transitionToRoute('tasks');
                }, function(){
                    self.get('controllers.application').hideLoading();
                    self.get('controllers.application').error_message(
                            "Could not complete task!"
                    );
                });
            }
        },
        'delete_annotation': function(description) {
            var model = this.get('model');
            var self = this;
            var annotations = model.get('annotations');
            this.get('controllers.application').showLoading();

            for (var i = 0; i < annotations.length; i++) {
                if (annotations[i] === description) {
                    annotations.removeAt(i);
                }
            }
            model.set('annotations', annotations);
            model.save().then(function(model) {
                self.get('controllers.application').hideLoading();
                model.reload();
            }, function(reason) {
                model.rollback();
                self.get('controllers.application').hideLoading();
                self.get('controllers.application').error_message(
                    "Could not delete annotation!"
                );
            });
        },
        'start': function() {
            var model = this.get('model');
            var self = this;
            var url = this.store.adapterFor('task').buildURL('task', model.get('uuid')) + 'start/';
            this.get('controllers.application').showLoading();
            $.ajax({
                url: url,
                type: 'POST',
                success: function() {
                    model.reload();
                },
                error: function() {
                    self.get('controllers.application').error_message(
                        "Could not start task!"
                    );
                    model.reload();
                },
                complete: function(){
                    self.get('controllers.application').hideLoading();
                }
            });
        },
        'stop': function() {
            var model = this.get('model');
            var self = this;
            this.get('controllers.application').showLoading();
            var url = this.store.adapterFor('task').buildURL('task', model.get('uuid')) + 'stop/';
            $.ajax({
                url: url,
                type: 'POST',
                success: function() {
                    model.reload();
                },
                error: function() {
                    self.get('controllers.application').error_message(
                        "Could not stop task!"
                    );
                    model.reload();
                },
                complete: function(){
                    self.get('controllers.application').hideLoading();
                }
            });
        },
        'delete': function(){
            var result = confirm("Are you sure you would like to delete this task?");
            if(result) {
                var self = this;
                var model = this.get('model');
                var url = this.store.adapterFor('task').buildURL('task', this.get('uuid')) + 'delete/';
                this.get('controllers.application').showLoading();
                $.ajax({
                    url: url,
                    type: 'POST',
                    success: function(){
                        model.reload();
                        self.get('controllers.tasks').refresh();
                        self.transitionToRoute('tasks');
                    },
                    error: function() {
                        self.get('controllers.application').error_message(
                            "Could not delete task!"
                        );
                        model.reload();
                    },
                    complete: function(){
                        self.get('controllers.application').hideLoading();
                    }
                });
            }
        }
    }
});

export default controller;
