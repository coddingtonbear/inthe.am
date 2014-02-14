var controller = Ember.Controller.extend({
  needs: ['tasks', 'activityLog'],
  user: null,
  urls: {
    about: '/about/',
    ca_certificate: '/api/v1/user/ca-certificate/',
    my_certificate: '/api/v1/user/my-certificate/',
    my_key: '/api/v1/user/my-key/',
    taskrc_extras: '/api/v1/user/taskrc/',
    taskd_settings: '/api/v1/user/configure-taskd/',
    taskd_reset: '/api/v1/user/reset-taskd-configuration/',
    twilio_integration: '/api/v1/user/twilio-integration/',
    tos_accept: '/api/v1/user/tos-accept/',
    status_feed: '/status/',
    sms_url: null,
  },
  update_user_info: function() {
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
    if(this.get('user').logged_in){
      Raven.setUser({
        email: this.get('user').email,
        id: this.get('user').uid,
        username: this.get('user').username
      });
    } else {
      Raven.setUser();
    }
    this.set('urls.sms_url', this.get('user').sms_url);
  },
  init: function(){
    var self = this;

    // Set up error reporting
    Ember.onerror = reportError;
    Ember.RSVP.configure('onerror', reportError);

    // Fetch user information
    this.update_user_info();

    // Ensure that we always add the CSRF token
    $.ajaxSetup({
      headers: {
        'X-CSRFToken': this.getCookie('csrftoken')
      }
    });

    // Set up the event stream
    if(window.EventSource) {
      var statusUpdater = new EventSource(this.get('urls.status_feed'));
      this.bindStatusActions(statusUpdater);
      this.set('statusUpdater', statusUpdater);
    } else {
      $('#refresh-link').show();
    }

    $(window).on('swiperight', function(event){
      if (self.get('user') && self.get('user').logged_in) {
        self.transitionToRoute('tasks');
      }
    });
  },
  bindStatusActions: function(updater) {
      for (var key in this.get('statusActions')) {
        updater.addEventListener(key, this.get('statusActions')[key].bind(this));
      }
  },
  statusActions: {
    'task_changed': function(evt) {
      Ember.run.once(this, function(){
        this.store.find('task', evt.data).then(function(record){
          if (record.get('isLoaded') && (!record.get('isDirty') && !record.get('isSaving'))) {
            record.reload();
          }
        });
      });
    },
    'head_changed': function(evt) {
      this.get('statusUpdater').close();
      var statusUpdater = new EventSource(this.get('urls.status_feed') + '?head=' + evt.data);
      this.bindStatusActions(statusUpdater);
      this.set('statusUpdater', statusUpdater);
    }
  },
  isSmallScreen: function() {
    return $(document).width() <= 700;
  },
  getCookie: function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  },
  actions: {
    refresh: function(){
      this.get('controllers.tasks').refresh();
    },
    home: function(){
      window.location = '/';
    },
    login: function(){
      window.location = '/login/google-oauth2/';
    },
    logout: function(){
      window.location = '/logout/';
    }
  }
});

module.exports = controller;
