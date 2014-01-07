var controller = Ember.ObjectController.extend({
  actions: {
    'complete': function(){
      var url = this.store.adapterFor('task').buildURL('task', this.get('uuid')) + 'complete/';
      var self = this;
      $.ajax({
        url: url,
        dataType: 'json',
        statusCode: {
          200: function(){
            self.get('model').unloadRecord();
            self.transitionToRoute('tasks');
          },
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
