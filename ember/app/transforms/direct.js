import DS from "ember-data";

export default DS.Transform.extend({
  serialize: function (value) {
    return value;
  },
  deserialize: function (value) {
    return value;
  },
});
