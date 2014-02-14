var route = Ember.Route.extend({
  model: function(params) {
     return this.store.find('task', params.uuid);
  },
  actions: {
    'edit': function(){
      if (this.controllerFor('application').isSmallScreen()) {
        this.transitionTo('createTask', this.controllerFor('task').get('model'));
      } else {
        this.controllerFor('createTaskModal').set(
          'model',
          this.controllerFor('task').get('model')
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
    },
    'add_annotation': function(){
      this.controllerFor('create_annotation').set(
        'model',
        this.controllerFor('task').get('model')
      );
      var rendered = this.render(
          'create_annotation',
          {
            'into': 'application',
            'outlet': 'modal',
          }
      );
      Ember.run.next(null, function(){
        $(document).foundation();
        $("#new_annotation_form").foundation('reveal', 'open');
      });
    }
  }
});

module.exports = route;
