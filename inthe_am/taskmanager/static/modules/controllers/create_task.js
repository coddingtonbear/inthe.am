var controller = Ember.ObjectController.extend({
  needs: ['tasks'],
  priorities: [
    {short: '', long: '(none)'},
    {short: 'l', long: 'Low'},
    {short: 'm', long: 'Medium'},
    {short: 'h', long: 'High'},
  ],
  actions: {
    'save': function() {
      if (this.get('due')) {
        this.set('due', moment(this.get('due')).toDate());
      }
      var model = this.get('model');
      var self = this;
      model.save().then(function(){
        $('#new_task_form').foundation('reveal', 'close');
        Ember.run.next(self, function(){
          if (model.get('isDirty')) {
            model.save().then(function(){
              self.get('controllers.tasks').refresh();
              self.transitionToRoute('task', model);
            });
          } else {
            self.get('controllers.tasks').refresh();
            self.transitionToRoute('task', model);
          }
        });
      }, function(){
        alert("An error was encountered while saving your task.");
      });
    }
  }
});

module.exports = controller;
