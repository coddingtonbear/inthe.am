import Ember from "ember";

var controller = Ember.Controller.extend({
  applicationController: Ember.inject.controller("application"),
  mustAccept: Ember.computed("applicationController.user", function () {
    let appCtrl = this.get("applicationController");
    return appCtrl.get("user.logged_in") && !appCtrl.get("user.tos_up_to_date");
  }),
  actions: {
    accept: function (version) {
      return this.get("applicationController")
        .ajaxRequest({
          url: this.get("applicationController").urls.tos_accept,
          type: "POST",
          data: {
            version: version,
          },
        })
        .then(
          function () {
            this.get("applicationController").handlePostLoginRedirects();
            this.transitionToRoute("getting-started");
            this.get("applicationController").update_user_info();
          }.bind(this),
          function (msg) {
            this.get("applicationController").error_message(
              `An error was encountered while ` +
                `attempting to accept the terms of service: ${msg}`
            );
          }.bind(this)
        );
    },
  },
});

export default controller;
