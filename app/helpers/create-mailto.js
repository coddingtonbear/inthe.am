import Ember from "ember";

export default Ember.Helper.helper(function([emailAddress, label]) {
    if(typeof(label) === 'object') {
        option = label;
    }
    if(option.hash.suffix) {
        var emailAddressParts = emailAddress.split('@');
        emailAddress = [
            emailAddressParts[0],
            option.hash.suffix,
            '@',
            emailAddressParts[1],
        ].join('');
    }
    emailAddress = Ember.Handlebars.Utils.escapeExpression(emailAddress);
    label = (arguments.length === 2) ? emailAddress : Ember.Handlebars.Utils.escapeExpression(label);

    var link = '<a href="mailto:' + emailAddress + '">' + label + '</a>';
    return new Ember.Handlebars.SafeString(link);
});
