import ArrayController from "ember-legacy-controllers/array";

var controller = ArrayController.extend({
  refresh: function () {
    try {
      this.get("content").update();
    } catch (e) {
      // Nothing to worry about -- probably just not loaded.
    }
  },
});

export default controller;
