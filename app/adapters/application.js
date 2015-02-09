import DS from "ember-data";

var KANBAN_ID_URL_RE = window.RegExp(".*kanban/([a-f0-9-]{36})");

export default DS.DjangoTastypieAdapter.extend({
    namespace: 'api/v1',
    buildURL: function(type, id, record) {
        var result = this._super(type, id, record);
        if(type === "kanbanTask") {
            var matched = KANBAN_ID_URL_RE.exec(window.location.href);
            var board_id = Ember.KANBAN_BOARD_ID;
            if (matched) {
                board_id = matched[1];
            }
            result = "/api/v1/kanban/" + board_id + "/";
            if (id) {
                result = result + id + "/";
            }
            return result;
        }
        return result;
    }
});
