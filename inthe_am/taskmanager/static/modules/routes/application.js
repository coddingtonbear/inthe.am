var route = Ember.Route.extend({
  actions: {
    'create_task': function() {
      this.controllerFor('create_task').set(
        'model',
        this.store.createRecord('task', {})
      );
      var rendered = this.render(
        'create_task',
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
