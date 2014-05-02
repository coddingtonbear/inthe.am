var controller = Ember.Controller.extend({
  needs: ['tasks', 'activityLog', 'configure'],
  user: null,
  urls: {
    login: '/login/google-oauth2/',
    logout: '/logout/',
    about: '/about/',
    ca_certificate: '/api/v1/user/ca-certificate/',
    my_certificate: '/api/v1/user/my-certificate/',
    my_key: '/api/v1/user/my-key/',
    taskrc_extras: '/api/v1/user/taskrc/',
    taskd_settings: '/api/v1/user/configure-taskd/',
    taskd_reset: '/api/v1/user/reset-taskd-configuration/',
    twilio_integration: '/api/v1/user/twilio-integration/',
    tos_accept: '/api/v1/user/tos-accept/',
    clear_task_data: '/api/v1/user/clear-task-data/',
    set_colorscheme: '/api/v1/user/colorscheme/',
    enable_sync: '/api/v1/user/enable-sync/',
    configure_pebble_cards: '/api/v1/user/pebble-cards-config/',
    configure_feed: '/api/v1/user/feed-config/',
    refresh: '/api/v1/task/refresh/',
    status_feed: '/status/',
    feed_url: null,
    sms_url: null,
    pebble_card_url: null,
  },
  taskUpdateStreamEnabled: function() {
    return this.get('controllers.configure.taskUpdateStreamEnabled');
  }.property(),
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
    this.updateColorscheme();
    if(this.get('user').logged_in){
      Raven.setUser({
        email: this.get('user').email,
        id: this.get('user').uid,
        username: this.get('user').username
      });
    } else {
      Raven.setUser();
    }
    this.set('urls.feed_url', this.get('user').feed_url);
    this.set('urls.sms_url', this.get('user').sms_url);
    this.set('urls.pebble_card_url', this.get('user').pebble_card_url);
    this.set('statusUpdaterHead', this.get('user').repository_head);
  },
  handleError: function(reason, tsn) {
    if (reason.status == 401) {
      alert(
          [
            "We're sorry, but your session appears to have expired.\n",
            "Press OK log-in again.",
          ].join('\n')
      );
      window.location = this.get('urls.login');
    }
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

    // Adding FastClick
    window.addEventListener('load', function() {
      FastClick.attach(document.body);
    }, false);

    // Set up the event stream
    if(this.get('taskUpdateStreamEnabled')) {
      this.set('statusUpdaterLog', []);
      this.startEventStream();
      setInterval(this.checkStatusUpdater.bind(this), 500);
    }
    setInterval(this.checkLastUpdated.bind(this), 2000);
  },
  checkLastUpdated: function() {
    var lastHeartbeat = this.get('statusUpdaterHeartbeat');
    var lastRefresh = this.get('pollingRefresh');
    if (!lastRefresh) {
      lastRefresh = new Date();
      this.set('pollingRefresh', lastRefresh);
    }
    var interval = 60 * 2.5 * 1000; // 2.5 mins
    if((new Date() - Math.max(lastRefresh, lastHeartbeat | null)) > interval) {
      this.set('pollingRefresh', new Date());
      this.send('refresh');
    }
  },
  checkStatusUpdater: function() {
    var statusUpdater = this.get('statusUpdater');
    var connected = this.get('taskUpdateStreamConnected');
    var now = new Date();
    var lastHeartbeat = this.get('statusUpdaterHeartbeat');
    var flatlineDelay = 19 * 1000; // 19 seconds
    var postDisconnectDelay = 5 * 1000;  // 5 seconds
    if (!statusUpdater) {
      return;
    }
    if (!lastHeartbeat) {
      lastHeartbeat = now;
      this.set('statusUpdaterHeartbeat', lastHeartbeat);
    }
    if (
      (statusUpdater.readyState != window.EventSource.OPEN) ||
      ((now - lastHeartbeat) > flatlineDelay)
    ) {
      this.set('taskUpdateStreamConnected', false);
      this.set('statusUpdaterErrorred', true);
      var since = this.get('taskUpdateStreamConnectionLost');
      if (! since) {
        this.set('taskUpdateStreamConnectionLost', now);
      } else if(now - since > postDisconnectDelay) {
        statusUpdater.close();
        var log = this.get('statusUpdaterLog');
        log.pushObject(
            [now, 'Connection appears to be disconnected']
        );
        this.set('statusUpdaterErrorred', true);
        this.set('taskUpdateStreamConnectionLost', null);
        this.get('startEventStream').bind(this)();
      }
    } else if (
      (statusUpdater.readyState == window.EventSource.OPEN) &&
      !connected
    ) {
      this.set('taskUpdateStreamConnected', true);
      this.set('statusUpdaterErrorred', false);
    }
  },
  startEventStream: function() {
    var head = this.get('statusUpdaterHead');
    var log = this.get('statusUpdaterLog');
    this.set('statusUpdaterHeartbeat', new Date());
    log.pushObject(
      [new Date(), 'Starting with HEAD ' + head]
    );
    var statusUpdater = this.get('statusUpdater');
    if (
      this.get('taskUpdateStreamEnabled') &&
      (!statusUpdater || statusUpdater.readyState == window.EventSource.CLOSED)
    ){
      url = this.get('urls.status_feed');
      if(head && typeof(head) == 'string') {
        url = url + "?head=" +  head;
      }
      statusUpdater = new window.EventSource(url);
      this.bindStatusActions(statusUpdater);
      this.set('statusUpdater', statusUpdater);
      this.set('statusUpdaterHead', head);
    } else {
      this.set('taskUpdateStreamConnected', false);
    }
  },
  eventStreamError: function(evt) {
    this.get('startEventStream').bind(this)();
  },
  updateColorscheme: function() {
    var scheme = this.get('user').colorscheme;
    $("#colorscheme").attr('href', '/static/colorschemes/' + scheme + '.css');
  },
  bindStatusActions: function(updater) {
    for (var key in this.get('statusActions')) {
      updater.addEventListener(key, this.get('statusActions')[key].bind(this));
    }
    updater.addEventListener(
      'error',
      this.get('eventStreamError').bind(this)
    );
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
      var statusUpdater = this.get('statusUpdater');
      if (statusUpdater) {
        statusUpdater.close();
        this.get('startEventStream').bind(this)();
      }
      this.set('statusUpdaterHead', evt.data);
      try {
        this.store.find('activityLog').update();
      } catch(e) {
        // Pass
      }
    },
    'error_logged': function(evt) {
      $.growl.error({
        title: 'Error',
        message: evt.data
      });
    },
    'heartbeat': function(evt) {
      this.set('statusUpdaterHeartbeat', new Date());
      var heartbeat_data = JSON.parse(evt.data);
      this.set('user.sync_enabled', heartbeat_data.sync_enabled);
    }
  },
  isSmallScreen: function() {
    return $(document).width() <= 800;
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
      var self = this;
      $.ajax({
        url: this.get('urls.refresh'),
        dataType: 'json',
        data: {
          head: this.get('statusUpdaterHead'),
        },
        success: function(data) {
          for(var i = 0; i < data.messages.length; i++) {
            var msg = data.messages[i];
            self.get('statusActions')[msg.action].bind(self)({data: msg.body});
          }
        }
      });
    },
    home: function(){
      window.location = '/';
    },
    login: function(){
      window.location = this.get('urls.login');
    },
    logout: function(){
      window.location = this.get('urls.logout');
    }
  }
});

module.exports = controller;
