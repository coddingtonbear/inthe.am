import Ember from "ember";

var route = Ember.Route.extend({
    model: function(params) {
        var invitation_url = this.controllerFor('kanban-board').getBoardUrl(
            "members/" + params.invitation_uuid + "/",
            params.board_uuid
        );
        return this.controllerFor('application').ajaxRequest({
            'url': invitation_url
        }).then(function(data){
            return data;
        });
    }
});

export default route;
