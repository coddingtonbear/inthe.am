import Ember from 'ember';

var route = Ember.Route.extend({
    renderTemplate: function(){
        if(window.location.hostname === 'inthe.am') {
            this.render('about');
        } else {
            this.render('about-local');
        }
    }
});

export default route;
