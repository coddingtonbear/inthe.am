var controller = Ember.Controller.extend({
  needs: ['application'],
  actions: {
    accept: function(version) {
      var self = this;
      $.ajax({
        url: this.get('controllers.application').urls.tos_accept,
        type: 'POST',
        data: {
          version: version
        },
        success: function() {
          self.get('controllers.application').update_user_info();
          self.transitionToRoute('tasks');
        },
        error: function() {
          alert(
            "An error was encountered while accepting the terms of service. Please try again later."
          );
        }
      });
    }
  }
});

module.exports = controller;
