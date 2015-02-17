import Ember from "ember";

var route = Ember.Route.extend({
    model: function(){
        var application = this.controllerFor('application');
        application.showLoading();
        return this.store.find('kanban-task').then(function(data){
            application.hideLoading();
            return data;
        });
    },
    actions: {
        invite_user: function() {
            var rendered = this.render(
                'invite-user-to-kanban-board',
                {
                    into: 'application',
                    outlet: 'modal'
                }
            );
            Ember.run.next(null, function(){
                $(document).foundation();
                $("#invite_user_form").foundation('reveal', 'open');
                setTimeout(function(){$("input[name=description]").focus();}, 500);
            });
            return rendered;
        }
    }
});

export default route;
