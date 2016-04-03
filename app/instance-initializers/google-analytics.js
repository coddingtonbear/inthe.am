import GoogleAnalyticsTrackingMixin from '../mixins/google-analytics';
import Ember from 'ember';

export function initialize(applicationInstance) {
    Ember.Router.reopen(GoogleAnalyticsTrackingMixin);

    /* jshint ignore:start */
    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
    ga('create', 'UA-3711530-3', 'inthe.am');
    ga('send', 'pageview');
    /* jshint ignore:end */

    var router = applicationInstance.lookup('router:main');
    router.on('didTransition', function() {
        this.trackPageView(this.get('url'));
    });
}
export default {
    name: "google-analytics",
    initialize: initialize
};
