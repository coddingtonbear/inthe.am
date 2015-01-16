import Ember from "ember";

var controller = Ember.ObjectController.extend({
    needs: ['application'],
    actions: {
        'save': function() {
            var self = this;
            var application = self.get('controllers.application');
            var model = this.get('model');
            var annotations = model.get('annotations');
            var field = $("#new_annotation_body");
            var form = $("#new_annotation_form");

            if (annotations === null) {
                annotations = [];
            }
            annotations.pushObject(field.val());
            model.set('annotations', annotations);
            application.showLoading();
            model.save().then(function(){
                application.hideLoading();
                field.val('');
                form.foundation('reveal', 'close');
            }, function() {
                application.hideLoading();
                application.error_message(
                    "An error was encountered while saving your annotation!"
                );
            });
        }
    }
});

export default controller;
