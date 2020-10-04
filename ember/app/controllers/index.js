import Ember from "ember";

var controller = Ember.Controller.extend({
  applicationController: Ember.inject.controller("application"),
  notifyUserLoaded: function () {
    var user = this.get("applicationController.user");
    var handler = this.get("applicationController").getHandlerPath();
    if (handler === "index" && user.logged_in) {
      if (this.get("applicationController").isSmallScreen()) {
        this.transitionToRoute("mobile-tasks");
      } else {
        this.transitionToRoute("tasks");
      }
    }
  },
});

export default controller;
