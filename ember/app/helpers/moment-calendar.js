import Ember from "ember";

export default Ember.Helper.helper(function ([date]) {
  if (date) {
    return new Ember.Handlebars.SafeString(
      '<span class="calendar date" title="' +
        moment(date).format("LLLL") +
        '">' +
        moment(date).calendar() +
        "</span>"
    );
  }
});
