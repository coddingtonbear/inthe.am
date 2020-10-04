import DS from "ember-data";

var model = DS.Model.extend({
  name: DS.attr("string"),
  columns: DS.attr(),
});

export default model;
