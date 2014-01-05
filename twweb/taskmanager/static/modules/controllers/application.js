var controller = Ember.Controller.extend({
  user: null,
  urls: {
    logout: '/logout/',
    login: '/login/dropbox/'
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
