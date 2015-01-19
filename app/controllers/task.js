import Ember from "ember";

var controller = Ember.ObjectController.extend({
    needs: ['application', 'tasks'],
    ajaxRequest: function(params) {
        return this.get('controllers.application').ajaxRequest(params);
    },
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
        'delete_annotation': function(rawDescription) {
            var model = this.get('model');
            var self = this;
            var annotations = model.get('annotations');
            this.get('controllers.application').showLoading();

            // Sometimes, for some unknown reason, some browsers receive
            // the annotation value as an array-like object :-\
            var description = Array.prototype.join.call(rawDescription, '');

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
            var url = this.store.adapterFor('task').buildURL('task', model.get('uuid')) + 'start/';

            return this.ajaxRequest({
                url: url,
                type: 'POST'
            }).then(function(){
                model.reload();
            }.bind(this), function(msg){
                model.reload();
                this.get('controllers.application').error_message(
                    `An error was encountered while ` +
                    `attempting to start your task: ${msg}`
                );
            }.bind(this));
        },
        'stop': function() {
            var model = this.get('model');
            var url = this.store.adapterFor('task').buildURL('task', model.get('uuid')) + 'stop/';

            return this.ajaxRequest({
                url: url,
                type: 'POST',
            }).then(function(){
                model.reload();
            }.bind(this), function(msg){
                model.reload();
                this.get('controllers.application').error_message(
                    `An error was encountered while ` +
                    `attempting to stop your task: ${msg}`
                );
            }.bind(this));
        },
        'delete': function(){
            var result = confirm("Are you sure you would like to delete this task?");
            if(result) {
                var model = this.get('model');
                var url = this.store.adapterFor('task').buildURL('task', this.get('uuid')) + 'delete/';
                this.get('controllers.application').showLoading();

                return this.ajaxRequest({
                    url: url,
                    type: 'POST',
                }).then(function(){
                    model.reload();
                    this.get('controllers.tasks').refresh();
                    this.transitionToRoute('tasks');
                }.bind(this), function(msg){
                    model.reload();
                    this.get('controllers.application').error_message(
                        `An error was encountered while ` +
                        `attempting to delete your task: ${msg}`
                    );
                }.bind(this));
            }
        }
    }
});

export default controller;
