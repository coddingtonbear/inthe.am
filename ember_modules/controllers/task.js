var controller = Ember.ObjectController.extend({
  needs: ['application', 'tasks'],
  actions: {
    'complete': function(){
      var result = confirm("Are you sure you would like to mark this task as completed?");
      if(result) {
        var self = this;
        this.get('model').destroyRecord().then(function(){
          self.get('controllers.tasks').refresh();
          self.transitionToRoute('tasks');
        }, function(){
          this.get('controllers.application').error_message(
              "An error was encountered while deleting that annotation."
          );
        });
      }
    },
    'delete_annotation': function(description) {
      var model = this.get('model');
      var annotations = model.get('annotations');

      for (var i = 0; i < annotations.length; i++) {
        if (annotations[i] == description) {
          annotations.removeAt(i);
        }
      }
      model.set('annotations', annotations);
      model.save().then(function(model) {
        // Noop
      }, function(reason) {
        this.get('controllers.application').error_message(
          "Could not delete annotation!"
        );
        model.reload();
      });
    },
    'start': function() {
      var model = this.get('model');
      model.set('start', new Date());
      var url = this.store.adapterFor('task').buildURL('task', model.get('uuid')) + 'start/';
      $.ajax({
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function() {
          model.reload();
        },
        error: function() {
          this.get('controllers.application').error_message(
            "Could not start task!"
          );
          model.reload();
        }
      });
    },
    'stop': function() {
      var model = this.get('model');
      model.set('start', null);
      var url = this.store.adapterFor('task').buildURL('task', model.get('uuid')) + 'stop/';
      $.ajax({
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function() {
          model.reload();
        },
        error: function() {
          this.get('controllers.application').error_message(
            "Could not stop task!"
          );
          model.reload();
        }
      });
    },
    'delete': function(){
      var result = confirm("Are you sure you would like to delete this task?");
      if(result) {
        var self = this;
        var url = this.store.adapterFor('task').buildURL('task', this.get('uuid')) + 'delete/';
        $.ajax({
          url: url,
          dataType: 'json',
          type: 'POST',
          success: function(){
            self.get('model').unloadRecord();
            self.get('controllers.tasks').refresh();
            self.transitionToRoute('tasks');
          },
          error: function() {
            this.get('controllers.application').error_message(
              "Could not delete task!"
            );
            model.reload();
          }
        });
      }
    }
  }
});

module.exports = controller;
