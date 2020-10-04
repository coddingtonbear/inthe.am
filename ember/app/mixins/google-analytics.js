import Ember from "ember";

var mixin = Ember.Mixin.create({
  pageHasGa: function () {
    return window.ga && typeof window.ga === "function";
  },

  trackPageView: function (page) {
    if (this.pageHasGa()) {
      if (!page) {
        var loc = window.location;
        page = loc.hash ? loc.hash.substring(1) : loc.pathname + loc.search;
      }

      ga("send", "pageview", page);
    }
  },

  trackEvent: function (category, action) {
    if (this.pageHasGa()) {
      ga("send", "event", category, action);
    }
  },
});

export default mixin;
