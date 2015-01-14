import Ember from "ember";

export default Ember.Handlebars.makeBoundHelper(function(html) {
    return new Ember.Handlebars.SafeString(
        linkify(markdown.toHTML(html))
    );
});
