var controller = Ember.Controller.extend({
  needs: ['tasks'],
  user: null,
  urls: {
    ca_certificate: '/api/v1/user/ca-certificate/',
    my_certificate: '/api/v1/user/my-certificate/',
    my_key: '/api/v1/user/my-key/',
    taskrc_extras: '/api/v1/user/taskrc/',
    taskd_settings: '/api/v1/user/configure-taskd/',
    taskd_reset: '/api/v1/user/reset-taskd-configuration/',
    twilio_integration: '/api/v1/user/twilio-integration/',
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
    this.set('urls.sms_url', this.get('user').sms_url);
  },
  init: function(){
    var self = this;
    this.update_user_info();

    $.ajaxSetup({
      headers: {
        'X-CSRFToken': this.getCookie('csrftoken')
      }
    });

    if(EventSource) {
      var statusUpdater = new EventSource(this.get('urls.status_feed'));
      this.bindStatusActions(statusUpdater);
      this.set('statusUpdater', statusUpdater);
    }
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
  updateStyles: function(){
    if(this.currentPath.substring(0, 5) == "tasks") {
      $("body").css('overflow', 'hidden');
    } else {
      $("body").css('overflow', 'scroll');
    }
  }.observes('currentPath'),
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
