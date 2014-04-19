
App.User = require("./user.js");
App.Task = require("./task.js");
App.Activitylog = require("./activitylog.js");

App.DirectTransform = DS.Transform.extend({
  serialize: function(value) {
    return value;
  },
  deserialize: function(value) {
    return value;
  }
});
