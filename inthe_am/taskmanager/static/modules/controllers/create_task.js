var controller = Ember.ObjectController.extend({
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
              self.transitionToRoute('refresh');
            });
          } else {
            self.transitionToRoute('refresh');
          }
        });
      }, function(){
        alert("An error was encountered while saving your task.");
      });
    }
  }
});

module.exports = controller;
