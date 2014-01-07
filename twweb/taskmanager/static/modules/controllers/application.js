var controller = Ember.Controller.extend({
  user: null,
  pending_count: null,
  urls: {
    logout: '/logout/',
    login: '/login/dropbox-oauth2/'
  },
  init: function(){
    this.set(
      'user',
      JSON.parse(
        $.ajax(
          {
            url: '/api/v1/user/status/',
            async: false,
            dataType: 'json'
          }
        ).responseText
      )
    );
  }
});

module.exports = controller;
