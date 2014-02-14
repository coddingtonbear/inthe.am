var route = Ember.Route.extend({
  actions: {
    'create_task': function() {
      this.controllerFor('createTaskModal').set(
        'model',
        this.store.createRecord('task', {})
      );
      var rendered = this.render(
        'createTaskModal',
        {
          'into': 'application',
          'outlet': 'modal',
        }
      );
      Ember.run.next(null, function(){
        $(document).foundation();
        $("#new_task_form").foundation('reveal', 'open');
      });
      return rendered;
    }
  }
});

module.exports = route;
