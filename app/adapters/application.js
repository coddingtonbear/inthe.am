import DS from "ember-data";

var KANBAN_ID_URL_RE = window.RegExp(".*kanban/([a-f0-9-]{36})");

export default DS.DjangoTastypieAdapter.extend({
    namespace: 'api/v1',
});
