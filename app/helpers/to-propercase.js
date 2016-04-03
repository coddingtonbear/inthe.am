import Ember from "ember";

export default Ember.Helper.helper(function([project_name]) {
    if (project_name) {
        var properCase = function(txt) {
            return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
        };
        return project_name.replace('_', ' ').replace(/\w\S*/g, properCase);
    }
});
