var controller = Ember.ObjectController.extend({
  needs: ['application', 'tasks'],
  priorities: [
    {short: '', long: '(none)'},
    {short: 'L', long: 'Low'},
    {short: 'M', long: 'Medium'},
    {short: 'H', long: 'High'},
  ],
  actions: {
    'save': function() {
      var model = this.get('model');
      var self = this;
      $('#new_task_form').foundation('reveal', 'close');
      model.save().then(function(){
        self.transitionToRoute('task', model);
      }, function(reason){
        var application = self.get('controllers.application');
        application.get('handleError').bind(application)(reason);
      });
    }
  }
});

module.exports = controller;
