import Ember from "ember";
import ObjectController from 'ember-legacy-controllers/object'

var controller = ObjectController.extend({
    applicationController: Ember.inject.controller('application'),
    actions: {
        'save': function() {
            var application = this.get('applicationController');
            var model = this.get('model');
            var annotations = model.get('annotations');
            var field = $("#new_annotation_body");
            var form = $("#new_annotation_form");
            var value = field.val();

            if (annotations === null) {
                annotations = [];
            }
            if (!value) {
                // If they didn't enter any text into the annotation
                // form, just close the dialog and go about your day.
                application.closeModal(form);
                return;
            }

            annotations.pushObject(value);
            model.set('annotations', annotations);
            application.showLoading();
            model.save().then(function(){
                application.hideLoading();
                application.closeModal(form);
            }.bind(this), function(msg) {
                model.rollback();
                model.reload();
                application.hideLoading();
                application.error_message(
                    "An error was encountered while " +
                    "saving this annotation.  Check your " +
                    "Activity Log for more information."
                );
            }.bind(this));
        }
    }
});

export default controller;
