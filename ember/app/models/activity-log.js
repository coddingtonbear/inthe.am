import DS from "ember-data";
import Ember from "ember";

var model = DS.Model.extend({
  md5hash: DS.attr("string"),
  last_seen: DS.attr("date"),
  created: DS.attr("date"),
  error: DS.attr("boolean"),
  message: DS.attr("string"),
  count: DS.attr("number"),

  task_uuids: function () {
    var taskMatcher = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi;
    var match;
    var matches = Ember.ArrayProxy.create({ content: [] });
    while ((match = taskMatcher.exec(this.get("message")))) {
      if (matches.indexOf(match[0]) === -1) {
        matches.pushObject(match[0]);
      }
    }
    return matches;
  }.property("message"),
});

export default model;
