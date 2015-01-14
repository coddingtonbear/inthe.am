import Ember from "ember";

export default Ember.Handlebars.makeBoundHelper(function(project_name, options) {
    if (project_name) {
        var properCase = function(txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        };
        return project_name.replace('_', ' ').replace(/\w\S*/g, properCase);
    }
});
