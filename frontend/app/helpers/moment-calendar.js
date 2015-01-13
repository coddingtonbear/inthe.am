import Ember from "ember";

export default Ember.Handlebars.makeBoundHelper(function(date, options) {
    if (date) {
        return new Handlebars.SafeString('<span class="calendar date" title="' + moment(date).format('LLLL') + '">' + moment(date).calendar() + "</span>");
    }
});
