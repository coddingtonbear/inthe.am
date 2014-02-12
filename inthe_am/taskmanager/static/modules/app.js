var App = Ember.Application.create({
});

App.ApplicationAdapter = DS.DjangoTastypieAdapter.extend({
  namespace: 'api/v1',
});
App.ApplicationSerializer = DS.DjangoTastypieSerializer.extend({
});

module.exports = App;

Ember.View.reopen({
  didInsertElement: function() {
    this._super();
    Ember.run.scheduleOnce('afterRender', this, this.didRenderElement);
  },
  initializeFoundation: function(){
    Ember.run.debounce(
      this,
      function(){
        Ember.$(document).foundation();
      },
      250
    );
  },
  didRenderElement: function() {
    this.initializeFoundation();
  }
});

