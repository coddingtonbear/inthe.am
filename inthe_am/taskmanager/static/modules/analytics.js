Ember.GoogleAnalyticsTrackingMixin = Ember.Mixin.create({
  pageHasGa: function() {
    return window.ga && typeof window.ga === "function";
  },

  trackPageView: function(page) {
    debugger;
    if (this.pageHasGa()) {
      if (!page) {
        var loc = window.location;
        page = loc.hash ? loc.hash.substring(1) : loc.pathname + loc.search;
      }

      ga('send', 'pageview', page);
    }
  },

  trackEvent: function(category, action) {
    if (this.pageHasGa()) {
      ga('send', 'event', category, action);
    }
  }
});
Ember.Application.initializer({
  name: "googleAnalytics",

  initialize: function(container, application) {
    var router = container.lookup('router:main');
    router.on('didTransition', function() {
      this.trackPageView(this.get('url'));
    });
  }
});
Ember.Router.reopen(Ember.GoogleAnalyticsTrackingMixin);
