var controller = Ember.ObjectController.extend({
  needs: ['application'],
  init: function() {
    var self = this;
    Ember.run.next(self, function(){
      var url = self.get('controllers.application').urls.about;
      //window.location = url;
    });
  }
});

module.exports = controller;
