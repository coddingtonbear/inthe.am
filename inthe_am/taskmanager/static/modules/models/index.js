
App.User = require("./user.js");
App.Annotation = require("./annotation.js");
App.Task = require("./task.js");

App.TaskSerializer = DS.DjangoTastypieSerializer.extend({
  attrs: {
    tasks: {
      embedded: 'always'
    }
  }
});

App.DirectTransform = DS.Transform.extend({
  serialize: function(value) {
    return value;
  },
  deserialize: function(value) {
    return value;
  }
});
