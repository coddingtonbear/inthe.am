var controller = Ember.ObjectController.extend({
  needs: ['tasks'],
  actions: {
    'complete': function(){
      var self = this;
      this.get('model').destroyRecord().then(function(){
        self.get('controllers.tasks').refresh();
        self.transitionToRoute('tasks');
      }, function(){
        alert("An error was encountered while marking this task completed.");
      });
    },
    'delete_annotation': function(description) {
      var model = this.get('model');
      var annotations = model.get('annotations');

      for (var i = 0; i < annotations.length; i++) {
        if (annotations[i].description == description) {
          annotations.removeAt(i);
        }
      }
      model.set('annotations', annotations);
      model.save();
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
        }
      });
    },
    'delete': function(){
      var url = this.store.adapterFor('task').buildURL('task', this.get('uuid')) + 'delete/';
      $.ajax({
        url: url,
        dataType: 'json',
        statusCode: {
          200: function(){
            self.get('model').unloadRecord();
            self.get('controllers.tasks').refresh();
            self.transitionToRoute('tasks');
          },
          501: function(){
            alert("Deleting tasks is currently unimplemented");
          }
        }
      });
    }
  }
});

module.exports = controller;
