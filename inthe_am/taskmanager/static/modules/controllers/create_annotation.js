var controller = Ember.ObjectController.extend({
  actions: {
    'save': function() {
      var model = this.get('model');
      var annotations = model.get('annotations');
      var field = $("#new_annotation_body");
      var form = $("#new_annotation_form");

      if (annotations === null) {
        annotations = [];
      }
      annotations.pushObject({
        entry: new Date(),
        description: field.val()
      });
      model.set('annotations', annotations);
      model.save();

      field.val('');

      form.foundation('reveal', 'close');
    }
  }
});

module.exports = controller;
