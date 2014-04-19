var App = Ember.Application.create({
});

App.ApplicationAdapter = DS.DjangoTastypieAdapter.extend({
  namespace: 'api/v1',
});
App.ApplicationSerializer = DS.DjangoTastypieSerializer.extend({
});

module.exports = App;

var initializeFoundation = function() {
  Ember.$(document).foundation();
};

Ember.View.reopen({
  didInsertElement: function() {
    this._super();
    Ember.run.debounce(
      null,
      initializeFoundation,
      500
    );
  },
});

