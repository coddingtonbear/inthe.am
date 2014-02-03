var route = Ember.Route.extend({
  model: function(params) {
     return this.store.find('task', params.uuid);
  },
  actions: {
    'edit': function(){
      this.controllerFor('create_task').set(
        'model',
        this.controllerFor('task').get('model')
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
    },
  }
});

module.exports = route;
