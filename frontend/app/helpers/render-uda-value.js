import Ember from "ember";

export default Ember.Handlebars.makeBoundHelper(function(uda) {
    if(uda.type == 'DateField') {
        if (uda.value) {
            return new Handlebars.SafeString(
                '<span class="calendar date" title="' + moment(uda.value).format('LLLL') + '">' + moment(uda.value).calendar() + "</span>"
            );
        }
    } else if (uda.type == 'StringField') {
        return new Handlebars.SafeString(linkify(markdown.toHTML(uda.value)));
    }
    return uda.value;
});
