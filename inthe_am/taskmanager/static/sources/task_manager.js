(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);throw new Error("Cannot find module '"+o+"'")}var f=n[o]={exports:{}};t[o][0].call(f.exports,function(e){var n=t[o][1][e];return s(n?n:e)},f,f.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
Ember.GoogleAnalyticsTrackingMixin = Ember.Mixin.create({
  pageHasGa: function() {
    return window.ga && typeof window.ga === "function";
  },

  trackPageView: function(page) {
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

},{}],2:[function(require,module,exports){
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


},{}],3:[function(require,module,exports){
var controller = Ember.Controller.extend({
  needs: ['application'],
  urls: {
    web_ui: '/static/about/web_ui.png',
    mobile: '/static/about/mobile.png'
  },
  actions: {
    login: function(){
      window.location = this.get('controllers.application.urls.login');
    },
  }
});

module.exports = controller;

},{}],4:[function(require,module,exports){
var controller = Ember.ArrayController.extend({
  refresh: function(){
    try {
      this.get('content').update();
    } catch (e) {
      // Nothing to worry about -- probably just not loaded.
    }
  },
});

module.exports = controller;

},{}],5:[function(require,module,exports){
var controller = Ember.Controller.extend({
  needs: ['application']
});

module.exports = controller;

},{}],6:[function(require,module,exports){
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
    $("body").touchwipe({
      wipeRight: function() {
        if (self.isSmallScreen()) {
          self.transitionToRoute('mobileTasks');
        }
      },
      min_move_x: 100,
      preventDefaultEvents: false
    });
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

},{}],7:[function(require,module,exports){
var controller = Ember.ArrayController.extend({
  sortProperties: ['-modified'],
  sortAscending: false,

  actions: {
    view_task: function(task){
      this.transitionToRoute('completedTask', task);
    }
  },
});

module.exports = controller;

},{}],8:[function(require,module,exports){
var controller = Ember.ObjectController.extend();

module.exports = controller;

},{}],9:[function(require,module,exports){
var controller = Ember.Controller.extend({
  needs: ['application'],
  taskd_trust_settings: [
    {short: 'no', long: 'Validate taskd server using an uploaded CA Certificate'},
    {short: 'yes', long: 'Trust taskd server implicitly; do not validate using a CA Certificate'},
  ],
  taskUpdateStringSettings: [
    {short: 'no', long: 'Disabled'},
    {short: 'yes', long: 'Enabled'},
  ],
  pebbleCardsEnabledUI: [
    {value: false, human: 'Disabled'},
    {value: true, human: 'Enabled'},
  ],
  feedEnabledUI: [
    {value: false, human: 'Disabled'},
    {value: true, human: 'Enabled'},
  ],
  themeOptions: [
    {file: 'light-16.theme', name: 'Light (4-bit)'},
    {file: 'dark-16.theme', name: 'Dark (4-bit)'},
    {file: 'light-256.theme', name: 'Light'},
    {file: 'dark-256.theme', name: 'Dark'},
    {file: 'dark-red-256.theme', name: 'Dark Red'},
    {file: 'dark-green-256.theme', name: 'Dark Green'},
    {file: 'dark-blue-256.theme', name: 'Dark Blue'},
    {file: 'dark-violets-256.theme', name: 'Dark Violet'},
    {file: 'dark-yellow-green.theme', name: 'Dark Yellow/Green'},
    {file: 'dark-gray-256.theme', name: 'Dark Gray'},
    {file: 'solarized-dark-256.theme', name: 'Solarized Dark'},
    {file: 'solarized-light-256.theme', name: 'Solarized Light'},
  ],
  taskUpdateStreamEnabledUI: function() {
    if(this.get('taskUpdateStreamEnabled')) {
      return 'yes';
    } else {
      return 'no';
    }
  }.property(),
  taskUpdateStreamEnabled: function() {
    if(!this.get('taskUpdateStreamCompatible')) {
      return false;
    }
    if(window.localStorage.getItem('disable_ticket_stream')) {
      return false;
    }
    return true;
  }.property(),
  taskUpdateStreamCompatible: function() {
    if(!window.EventSource) {
      return false;
    }
    if(!window.localStorage) {
      return false;
    }
    return true;
  }.property(),
  submit_taskd: function(data) {
    if (
      data.certificate === false || data.key === false || data.ca === false
    ) {
      self.error_message("An error was encountered while uploading your files");
      return;
    } else if (
      !data.certificate || !data.key || (!data.ca && data.trust == 'no')
    ) {
      return;
    }
    var url = this.get('controllers.application').urls.taskd_settings;
    var csrftoken = this.get('controllers.application').getCookie(
      'csrftoken'
    );
    var self = this;

    $.ajax({
      url: url,
      type: 'POST',
      data: data,
      success: function(){
        self.get('controllers.application').update_user_info();
        self.success_message("Taskd settings saved.");
      },
      error: function(xhr){
        var response = JSON.parse(xhr.responseText);
        for (var property in response) {
          self.error_message(
            "Error encountered: " + property + ": " + response[property]
          );
        }
      }
    });
  },
  error_message: function(message) {
    $.growl.error({
      title: 'Error',
      message: message,
    });
  },
  success_message: function(message) {
    $.growl.notice({
      title: 'Success',
      message: message,
    });
  },
  actions: {
    save_taskrc: function() {
      var csrftoken = this.get('controllers.application').getCookie(
        'csrftoken'
      );
      var url = this.get('controllers.application').urls.taskrc_extras;
      var value = $('textarea[name=custom_taskrc]').val();
      var self = this;

      $.ajax({
        url: url,
        type: 'PUT',
        headers: {
          'X-CSRFToken': csrftoken
        },
        dataType: 'text',
        data: value,
        success: function() {
          self.get('controllers.application').update_user_info();
          self.success_message("Taskrc settings saved");
        },
        error: function() {
          self.error_message("An error was encountered while saving your taskrc settings.");
        }
      });
    },
    reset_taskd: function() {
      var csrftoken = this.get('controllers.application').getCookie(
        'csrftoken'
      );
      var url = this.get('controllers.application').urls.taskd_reset;
      var self = this;
      $.ajax({
        url: url,
        type: 'POST',
        headers: {
          'X-CSRFToken': csrftoken
        },
        data: {},
        success: function(){
          self.get('controllers.application').update_user_info();
          self.success_message("Taskd settings reset to default.");
        },
        error: function(xhr){
          self.error_message(
            "Error encountered while resetting taskd settings to defaults."
          );
        }
      });
    },
    save_taskd: function() {
      var data = {
        server: document.getElementById('id_server').value,
        credentials: document.getElementById('id_credentials').value,
        trust: document.getElementById('id_trust').value,
      };
      var self = this;

      // Load Cert
      var cert_reader = new FileReader();
      cert_reader.onload = function(evt){
        data.certificate = evt.target.result;
        self.submit_taskd(data);
      };
      cert_reader.onerror = function(evt) {
        data.certificate = false;
        self.submit_taskd(data);
      };
      cert_reader.onabort = function(evt) {
        data.certificate = false;
        self.submit_taskd(data);
      };
      var cert_file = document.getElementById('id_certificate').files[0];
      if (cert_file === undefined) {
        self.error_message("Please select a certificate");
      }
      cert_reader.readAsBinaryString(cert_file);

      // Load Key
      var key_reader = new FileReader();
      key_reader.onload = function(evt){
        data.key = evt.target.result;
        self.submit_taskd(data);
      };
      key_reader.onerror = function(evt) {
        data.key = false;
        self.submit_taskd(data);
      };
      key_reader.onabort = function(evt) {
        data.key = false;
        self.submit_taskd(data);
      };
      var key_file = document.getElementById('id_key').files[0];
      if (key_file === undefined) {
        self.error_message("Please select a key");
      }
      key_reader.readAsBinaryString(key_file);

      // Load CA Certificate
      if (data.trust === 'no') {
        var ca_reader = new FileReader();
        ca_reader.onload = function(evt){
          data.ca = evt.target.result;
          self.submit_taskd(data);
        };
        ca_reader.onerror = function(evt) {
          data.ca = false;
          self.submit_taskd(data);
        };
        ca_reader.onabort = function(evt) {
          data.ca = false;
          self.submit_taskd(data);
        };
        var ca_file = document.getElementById('id_ca').files[0];
        if (ca_file === undefined) {
          self.error_message("Please select a CA Certificate");
        }
        ca_reader.readAsBinaryString(ca_file);
      }
    },
    save_twilio: function() {
      var data = {
        'twilio_auth_token': document.getElementById('id_twilio_auth_token').value,
        'sms_whitelist': document.getElementById('id_sms_whitelist').value
      };
      var url  = this.get('controllers.application').urls.twilio_integration;
      var self = this;

      $.ajax({
        url: url,
        type: 'POST',
        data: data,
        success: function() {
          self.success_message("Twilio settings saved.");
        },
        error: function() {
          var response = JSON.parse(xhr.responseText);
          for (var property in response) {
            self.error_message(
              "Error encountered: " + property + ": " + response[property]
            );
          }
        }
      });
    },
    save_streaming: function() {
      if($("#id_update_stream").val() === 'no') {
        window.localStorage.setItem('disable_ticket_stream', 'yes');
      } else {
        window.localStorage.removeItem('disable_ticket_stream');
      }
      window.location.reload();
    },
    clear_task_data: function() {
      var url  = this.get('controllers.application').urls.clear_task_data;
      var self = this;

      $.ajax({
        url: url,
        type: 'POST',
        success: function() {
          self.success_message("Task data cleared");
          setTimeout(function(){
            window.location.reload();
          }, 3000);
        },
        error: function() {
          var response = JSON.parse(xhr.responseText);
          for (var property in response) {
            self.error_message(
              "Error encountered: " + property + ": " + response[property]
            );
          }
        }
      });
    },
    save_colorscheme: function() {
      var value = $('#id_theme').val();
      var url  = this.get('controllers.application').urls.set_colorscheme;
      var self = this;
      $.ajax({
        url: url,
        type: 'PUT',
        data: value,
        success: function() {
          self.set('controllers.application.user.colorscheme', value);
          self.get('controllers.application').updateColorscheme();
          self.success_message("Colorscheme saved!");
        },
        error: function() {
          self.error_message(
            "An error was encountered while setting your colorscheme."
          );
        }
      });
    },
    save_feed: function(value) {
      var url  = this.get('controllers.application').urls.configure_feed;
      var enabled = false;
      if(typeof(value) != 'undefined') {
        enabled = value;
      } else if($("#id_feed_config").val() === true) {
        enabled = true;
      }
      var self = this;
      $.ajax({
        url: url,
        type: 'POST',
        data: {
          enabled: enabled ? 1 : 0,
        },
        success: function() {
          self.set('controllers.application.user.feed_enabled', enabled);
          if(enabled) {
            self.success_message("Feed enabled!");
          } else {
            self.success_message("Feed disabled!");
          }
        },
        error: function() {
          self.error_message(
            "An error was encountered while enabling your feed."
          );
        }
      });
    },
    save_pebble_cards: function(value) {
      var url  = this.get('controllers.application').urls.configure_pebble_cards;
      var enabled = false;
      if(typeof(value) != 'undefined') {
        enabled = value;
      }
      else if($("#id_pebble_cards_config").val() === true) {
        enabled = true;
      }
      var self = this;
      $.ajax({
        url: url,
        type: 'POST',
        data: {
          enabled: enabled ? 1 : 0,
        },
        success: function() {
          self.set('controllers.application.user.pebble_cards_enabled', enabled);
          if(enabled) {
            self.success_message("Pebble Cards URL enabled!");
          } else {
            self.success_message("Pebble Cards URL disabled!");
          }
        },
        error: function() {
          self.error_message(
            "An error was encountered while enabling your Pebble Cards URL."
          );
        }
      });
    },
    enable_sync: function() {
      var url  = this.get('controllers.application').urls.enable_sync;
      var self = this;
      $.ajax({
        url: url,
        type: 'POST',
        success: function() {
          self.set('controllers.application.user.sync_enabled', true);
          self.success_message("Sync re-enabled!");
        },
        error: function() {
          self.error_message(
            "An error was encountered while enabling sync."
          );
        }
      });
    }
  }
});

module.exports = controller;

},{}],10:[function(require,module,exports){
var controller = App.EditTaskController.extend();

module.exports = controller;

},{}],11:[function(require,module,exports){
var controller = Ember.ObjectController.extend({
  actions: {
    'save': function() {
      var model = this.get('model');
      var annotations = model.get('annotations');
      var field = $("#new_annotation_body");
      var form = $("#new_annotation_form");

      if (annotations === null) {
        annotations = [];
      }
      annotations.pushObject({
        entry: new Date(),
        description: field.val()
      });
      model.set('annotations', annotations);
      model.save();

      field.val('');

      form.foundation('reveal', 'close');
    }
  }
});

module.exports = controller;

},{}],12:[function(require,module,exports){
var controller = Ember.ObjectController.extend({
  needs: ['application', 'tasks'],
  priorities: [
    {short: '', long: '(none)'},
    {short: 'L', long: 'Low'},
    {short: 'M', long: 'Medium'},
    {short: 'H', long: 'High'},
  ],
  actions: {
    'save': function() {
      var model = this.get('model');
      var self = this;
      $('#new_task_form').foundation('reveal', 'close');
      model.save().then(function(){
        self.transitionToRoute('task', model);
      }, function(reason){
        var application = self.get('controllers.application');
        application.get('handleError').bind(application)(reason);
      });
    }
  }
});

module.exports = controller;

},{}],13:[function(require,module,exports){

App.ApplicationController = require("./application");
App.ActivityLogController = require("./activitylog");
App.TaskController = require("./task");
App.TasksController = require("./tasks");
App.MobileTasksController = require("./mobileTasks");
App.CompletedController = require("./completed");
App.CompletedTaskController = require("./completedTask");
App.AboutController = require("./about");
App.ApiDocsController = require("./apiDocs");
App.ConfigureController = require("./configure");
App.EditTaskController = require("./editTask");
App.CreateTaskController = require("./createTask");
App.CreateTaskModalController = require("./editTask");
App.CreateAnnotationController = require("./create_annotation");
App.TermsOfServiceController = require("./termsOfService");

App.IndexController = Ember.Controller.extend({
  needs: ["application"],
  init: function(){
    var user = this.get('controllers.application').user;
    var configured = user.configured;
    var self = this;
    if (! user.logged_in) {
      self.transitionToRoute('about');
    } else {
      self.transitionToRoute('tasks');
    }
  }
});

},{"./about":3,"./activitylog":4,"./apiDocs":5,"./application":6,"./completed":7,"./completedTask":8,"./configure":9,"./createTask":10,"./create_annotation":11,"./editTask":12,"./mobileTasks":14,"./task":15,"./tasks":16,"./termsOfService":17}],14:[function(require,module,exports){
var controller = App.TasksController.extend({});

module.exports = controller;

},{}],15:[function(require,module,exports){
var controller = Ember.ObjectController.extend({
  needs: ['tasks'],
  actions: {
    'complete': function(){
      var result = confirm("Are you sure you would like to mark this task as completed?");
      if(result) {
        var self = this;
        this.get('model').destroyRecord().then(function(){
          self.get('controllers.tasks').refresh();
          self.transitionToRoute('tasks');
        }, function(){
          alert("An error was encountered while marking this task completed.");
        });
      }
    },
    'delete_annotation': function(description) {
      var model = this.get('model');
      var annotations = model.get('annotations');

      for (var i = 0; i < annotations.length; i++) {
        if (annotations[i].description == description) {
          annotations.removeAt(i);
        }
      }
      model.set('annotations', annotations);
      model.save();
    },
    'start': function() {
      var model = this.get('model');
      model.set('start', new Date());
      var url = this.store.adapterFor('task').buildURL('task', model.get('uuid')) + 'start/';
      $.ajax({
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function() {
          model.reload();
        }
      });
    },
    'stop': function() {
      var model = this.get('model');
      model.set('start', null);
      var url = this.store.adapterFor('task').buildURL('task', model.get('uuid')) + 'stop/';
      $.ajax({
        url: url,
        dataType: 'json',
        type: 'POST',
        success: function() {
          model.reload();
        }
      });
    },
    'delete': function(){
      var result = confirm("Are you sure you would like to delete this task?");
      if(result) {
        var self = this;
        var url = this.store.adapterFor('task').buildURL('task', this.get('uuid')) + 'delete/';
        $.ajax({
          url: url,
          dataType: 'json',
          type: 'POST',
          success: function(){
            self.get('model').unloadRecord();
            self.get('controllers.tasks').refresh();
            self.transitionToRoute('tasks');
          }
        });
      }
    }
  }
});

module.exports = controller;

},{}],16:[function(require,module,exports){
var controller = Ember.ArrayController.extend({
  sortProperties: ['urgency'],
  sortAscending: false,
  refresh: function(){
    this.get('content').update();
  },
  pendingTasks: function() {
    var result = this.get('model').filterProperty('status', 'pending');

    var sortedResult = Em.ArrayProxy.createWithMixins(
      Ember.SortableMixin,
      {
        content:result,
        sortProperties: this.sortProperties,
        sortAscending: false
      }
    );
    return sortedResult;
  }.property('model.@each.status')
});

module.exports = controller;

},{}],17:[function(require,module,exports){
var controller = Ember.Controller.extend({
  needs: ['application'],
  actions: {
    accept: function(version) {
      var self = this;
      $.ajax({
        url: this.get('controllers.application').urls.tos_accept,
        type: 'POST',
        data: {
          version: version
        },
        success: function() {
          self.get('controllers.application').update_user_info();
          self.transitionToRoute('tasks');
        },
        error: function() {
          alert(
            "An error was encountered while accepting the terms of service. Please try again later."
          );
        }
      });
    }
  }
});

module.exports = controller;

},{}],18:[function(require,module,exports){
var field = Ember.TextField.extend({
  moment_format: 'YYYY-MM-DD HH:mm',
  picker_format: 'Y-m-d H:i',
  init: function() {
    this._super();
    this.updateModel();
  },
  updateModel: function(){
    var raw_value = this.get('date');
    var value = moment(raw_value);
    if (!raw_value || !value.isValid()) {
      this.set('value', '');
    } else {
      this.set('value', value.format(this.moment_format));
    }
  }.observes('identity'),
  updateDate: function(){
    var raw_value = this.get('value');
    if (raw_value.length === 0) {
      this.set('date', '');
    } else {
      var value = moment(raw_value);
      if (value.isValid()) {
        this.set('date', value.toDate());
      }
    }
  }.observes('value'),
  didInsertElement: function(){
    if($(document).width() > 350) {
      this.$().datetimepicker({
        format: this.picker_format,
        allowBlank: true
      });
    }
  }
});

module.exports = field;

},{}],19:[function(require,module,exports){
App.DateField = require("./date_field");
App.TagField = require("./tag_field");

},{"./date_field":18,"./tag_field":20}],20:[function(require,module,exports){
var field = Ember.TextField.extend({
  init: function() {
    this._super();
    this.updateModel();
  },
  updateModel: function(){
    var value = this.get('tags');
    if (!value) {
      this.set('value', '');
    } else {
      this.set('value', value.join(' '));
    }
  }.observes('identity'),
  updateDate: function(){
    var value = this.get('value');
    if (value.length === 0) {
      this.set('tags', []);
    } else {
      var newArray = [];
      var rawValues = value.split(' ');
      for (var i = 0; i < rawValues.length; i++) {
        if (rawValues[i] !== undefined && rawValues[i] !== null && rawValues[i] !== "") {
          newArray.push(rawValues[i]);
        }
      }
      this.set('tags', newArray);
    }
  }.observes('value'),
});

module.exports = field;

},{}],21:[function(require,module,exports){
var App = require('./app');

Ember.Handlebars.helper('comma_to_list', function(item, options){
  return item.split(',');
});

Ember.Handlebars.helper('propercase', function(project_name, options) {
  if (project_name) {
    var properCase = function(txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    };
    return project_name.replace('_', ' ').replace(/\w\S*/g, properCase);
  }
});

Ember.Handlebars.helper('calendar', function(date, options) {
  if (date) {
    return new Handlebars.SafeString('<span class="calendar date" title="' + moment(date).format('LLLL') + '">' + moment(date).calendar() + "</span>");
  }
});

Ember.Handlebars.helper('fromnow', function(date, options) {
  if (date) {
    return new Handlebars.SafeString('<span class="calendar date" title="' + moment(date).format('LLLL') + '">' + moment(date).fromNow() + "</span>");
  }
});

Ember.Handlebars.helper('markdown', function(html) {
  return new Handlebars.SafeString(markdown.toHTML(html));
});

},{"./app":2}],22:[function(require,module,exports){
App = require('./app');

require("./controllers");
require("./models");
require("./routes");
require("./views");
require("./helpers");
require("./fields");

},{"./app":2,"./controllers":13,"./fields":19,"./helpers":21,"./models":24,"./routes":36,"./views":44}],23:[function(require,module,exports){
var model = DS.Model.extend({
  md5hash: DS.attr('string'),
  last_seen: DS.attr('date'),
  created: DS.attr('date'),
  error: DS.attr('boolean'),
  message: DS.attr('string'),
  count: DS.attr('number'),

  task_uuids: function() {
    var taskMatcher = /[a-f0-9-]{36}/gi;
    var match;
    var matches = Ember.ArrayProxy.create({content: []});
    while(match = taskMatcher.exec(this.get('message'))) {
      if (matches.indexOf(match[0]) == -1) {
        matches.pushObject(match[0]);
      }
    }
    return matches;
  }.property('message')
});

module.exports = model;

},{}],24:[function(require,module,exports){

App.User = require("./user.js");
App.Task = require("./task.js");
App.Activitylog = require("./activitylog.js");

App.DirectTransform = DS.Transform.extend({
  serialize: function(value) {
    return value;
  },
  deserialize: function(value) {
    return value;
  }
});

},{"./activitylog.js":23,"./task.js":25,"./user.js":26}],25:[function(require,module,exports){
var model = DS.Model.extend({
  annotations: DS.attr(),
  tags: DS.attr(),
  description: DS.attr('string'),
  due: DS.attr('date'),
  entry: DS.attr('date'),
  modified: DS.attr('date'),
  priority: DS.attr('string'),
  resource_uri: DS.attr('string'),
  start: DS.attr('date'),
  wait: DS.attr('date'),
  scheduled: DS.attr('date'),
  'status': DS.attr('string'),
  urgency: DS.attr('number'),
  uuid: DS.attr('string'),
  depends: DS.attr('string'),
  blocks: DS.attr('string'),
  project: DS.attr('string'),
  imask: DS.attr('number'),
  udas: DS.attr(),

  editable: function(){
    if (this.get('status') == 'pending') {
      return true;
    }
    return false;
  }.property('status'),

  icon: function() {
    if (this.get('status') == 'completed') {
      return 'fa-check-circle-o';
    } else if (this.get('start')) {
      return 'fa-asterisk';
    } else if (this.get('due')) {
      return 'fa-clock-o';
    } else {
      return 'fa-circle-o';
    }
  }.property('status', 'start', 'due'),

  taskwarrior_class: function() {
    var value = '';
    if (this.get('start')) {
      value = 'active';
    } else if (this.get('is_blocked')) {
      value = 'blocked';
    } else if (this.get('is_blocking')) {
      value = 'blocking';
    } else if (moment(this.get('due')).isBefore(moment())) {
      value = 'overdue';
    } else if (moment().format('L') === moment(this.get('due')).format('L')) {
      value = 'due__today';
    } else if ( // Truncate date to date only
        moment(
          moment().format('YYYYMMDD'),
          'YYYYMMDD'
        ).add('days', 7).isAfter(this.get('due'))
    ) {
      value = 'due';
    } else if (this.get('imask')) {
      value = 'recurring';
    } else if (this.get('priority') == 'H') {
      value = 'pri__H';
    } else if (this.get('priority') == 'M') {
      value = 'pri__M';
    } else if (this.get('priority') == 'L') {
      value = 'pri__L';
    } else if (this.get('tags')) {
      value = 'tagged';
    }
    return value;
  }.property('status', 'urgency', 'start', 'due', 'is_blocked', 'is_blocking'),

  is_blocked: function() {
    return this.get('dependent_tickets').any(
      function(item, idx, enumerable) {
        if ($.inArray(item.get('status'), ['completed', 'deleted']) > -1) {
          return false;
        }
        return true;
      }
    );
  }.property('dependent_tickets'),

  is_blocking: function() {
    return this.get('blocked_tickets').any(
      function(item, idx, enumerable) {
        if ($.inArray(item.get('status'), ['completed', 'deleted']) > -1) {
          return false;
        }
        return true;
      }
    );
  }.property('blocked_tickets'),

  processed_annotations: function() {
    var value = this.get('annotations');
    if (value) {
      for (var i = 0; i < value.length; i++) {
        value[i] = {
          entry: new Date(Ember.Date.parse(value[i].entry)),
          description: value[i].description
        };
      }
    } else {
      return [];
    }
    return value;
  }.property('annotations'),

  processed_udas: function() {
    var value = [];
    for(var v in this.get('udas')) {
      value.push(this.get('udas')[v]);
    }
    return value;
  }.property('udas'),

  _string_field_to_data: function(field_name, for_property) {
    var cached_value = this.get('_' + field_name);
    var value = this.get(field_name);
    var values = [];
    if (cached_value !== undefined) {
      return cached_value;
    } else {
      this.set('_' + field_name, values);
    }
    if (value) {
      var ticket_ids = value.split(',');
      var add_value_to_values = function(value) {
        var _for_property = for_property;
        values.pushObject(value);
        this.propertyDidChange(_for_property);
      };
      for (var i = 0; i < ticket_ids.length; i++) {
        this.store.find('task', ticket_ids[i]).then(
          add_value_to_values.bind(this)
        );
      }
      return values;
    } else {
      return [];
    }
  },

  dependent_tickets: function(){
    return this._string_field_to_data('depends', 'dependent_tickets');
  }.property('depends'),

  blocked_tickets: function(){
    return this._string_field_to_data('blocks', 'blocked_tickets');
  }.property('blocks'),

  as_json: function() {
    return JSON.stringify(this.store.serialize(this));
  }.property()
});

module.exports = model;

},{}],26:[function(require,module,exports){
var model = DS.Model.extend({
  logged_in: DS.attr('boolean'),
  uid: DS.attr('string'),
  username: DS.attr('string'),
  name: DS.attr('string'),
  email: DS.attr('string'),
  configured: DS.attr('boolean'),
  taskd_credentials: DS.attr('string'),
  taskd_server: DS.attr('string'),
  api_key: DS.attr('string')
});

module.exports = model;

},{}],27:[function(require,module,exports){
App.Router.map(function(){
  this.route("login", {path: "/login"});
  this.route("about", {path: "/about"});
  this.resource("addToHomeScreen", {path: "/add-to-home-screen"});
  this.resource("mobileTasks", {path: "/mobile-tasks"});
  this.route("createTask", {path: "/create-task"});
  this.route("editTask", {path: "/edit-task/:uuid"});
  this.route("annotateTask", {path: "/annotate-task"});
  this.resource("tasks", function(){
    this.resource("task", {path: "/:uuid"});
  });
  this.resource("completed", function(){
    this.resource("completedTask", {path: "/:uuid"});
  });
  this.resource("activityLog", {path: "/activity-log"});
  this.route("unconfigurable", {path: "/no-tasks"});
  this.route("apiDocs", {path: "/api-documentation"});
  this.route("configure", {path: "/configure"});
  this.route("getting_started", {path: "/getting-started"});
  this.route("termsOfService", {path: "/terms-of-service"});
  this.route("fourOhFour", {path: "*path"});
});

App.Router.reopen({
  location: 'history'
});

},{}],28:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function() {
    return this.store.find('activitylog');
  }
});

module.exports = route;

},{}],29:[function(require,module,exports){
var route = Ember.Route.extend({
  afterModel: function(tasks, transition) {
    if($(document).width() > 700) {
      this.transitionTo('about');
    } else if (window.navigator.standalone) {
      this.transitionTo('mobileTasks');
    }
  }
});

module.exports = route;

},{}],30:[function(require,module,exports){
var route = Ember.Route.extend({
  actions: {
    'create_task': function() {
      this.controllerFor('createTaskModal').set(
        'model',
        this.store.createRecord('task', {})
      );
      var rendered = this.render(
        'createTaskModal',
        {
          'into': 'application',
          'outlet': 'modal',
        }
      );
      var displayModal = function(){
        $(document).foundation();
        $("#new_task_form").foundation('reveal', 'open');
        setTimeout(function(){$("input[name=description]").focus();}, 500);
      };
      Ember.run.scheduleOnce('afterRender', this, displayModal);
      return rendered;
    }
  }
});

module.exports = route;

},{}],31:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(){
    return this.store.findQuery('task', {completed: 1, order_by: '-modified'});
  }
});

module.exports = route;

},{}],32:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(params) {
    return this.store.find('task', params.uuid);
  },
  actions: {
    error: function(reason, tsn) {
      var application = this.controllerFor('application');
      application.get('handleError').bind(application)(reason, tsn);
    }
  }
});

module.exports = route;

},{}],33:[function(require,module,exports){
var route = Ember.Route.extend({
  setupController: function(controller) {
    model = this.store.createRecord('task', {});
    controller.set('model', model);
  },
  actions: {
    error: function(reason, tsn) {
      var application = this.controllerFor('application');
      application.get('handleError').bind(application)(reason, tsn);
    }
  }
});

module.exports = route;

},{}],34:[function(require,module,exports){
var route = Ember.Route.extend({
  setupController: function(controller, model) {
    controller.set('model', model);
  },
  actions: {
    error: function(reason, tsn) {
      var application = this.controllerFor('application');
      application.get('handleError').bind(application)(reason, tsn);
    }
  }
});

module.exports = route;

},{}],35:[function(require,module,exports){
var route = Ember.Route.extend({
  renderTemplate: function(_, error){
    this._super();
    var self = this;
  },
});

module.exports = route;

},{}],36:[function(require,module,exports){

App.IndexRoute = Ember.Route.extend({
  renderTemplate: function() {
    this.render('index');
  }
});
App.TaskRoute = require("./task");
App.TasksRoute = require("./tasks");
App.TasksIndexRoute = require("./tasks");
App.MobileTasksRoute = require("./mobileTasks");
App.CompletedRoute = require("./completed");
App.CompletedTaskRoute = require("./completedTask");
App.ActivityLogRoute = require("./activitylog");
App.ApplicationRoute = require("./application");
App.AddToHomeScreenRoute = require("./addToHomeScreen");
App.ErrorRoute = require("./error");
App.EditTaskRoute = require("./editTask");
App.CreateTaskRoute = require("./createTask");

},{"./activitylog":28,"./addToHomeScreen":29,"./application":30,"./completed":31,"./completedTask":32,"./createTask":33,"./editTask":34,"./error":35,"./mobileTasks":37,"./task":38,"./tasks":39}],37:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function() {
    return this.store.find('task');
  },
  actions: {
    error: function(reason, tsn) {
      var application = this.controllerFor('application');
      application.get('handleError').bind(application)(reason, tsn);
    }
  }
});

module.exports = route;

},{}],38:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function(params) {
     return this.store.find('task', params.uuid);
  },
  actions: {
    edit: function(){
      if (this.controllerFor('application').isSmallScreen()) {
        this.transitionTo('editTask', this.controllerFor('task').get('model'));
      } else {
        this.controllerFor('createTaskModal').set(
          'model',
          this.controllerFor('task').get('model')
        );
        var rendered = this.render(
          'createTaskModal',
          {
            'into': 'application',
            'outlet': 'modal',
          }
        );
        Ember.run.next(null, function(){
          $(document).foundation();
          $("#new_task_form").foundation('reveal', 'open');
        });
        return rendered;
      }
    },
    add_annotation: function(){
      this.controllerFor('create_annotation').set(
        'model',
        this.controllerFor('task').get('model')
      );
      var rendered = this.render(
          'create_annotation',
          {
            'into': 'application',
            'outlet': 'modal',
          }
      );
      Ember.run.next(null, function(){
        $(document).foundation();
        $("#new_annotation_form").foundation('reveal', 'open');
        setTimeout(function(){$("#new_annotation_body").focus();}, 500);
      });
    },
    error: function(reason, tsn) {
      var application = this.controllerFor('application');
      application.get('handleError').bind(application)(reason, tsn);
    }
  }
});

module.exports = route;

},{}],39:[function(require,module,exports){
var route = Ember.Route.extend({
  model: function() {
    return this.store.find('task');
  },
  beforeModel: function(tasks, transition) {
    var application = this.controllerFor('application');
    if(application.user.logged_in && !application.user.tos_up_to_date) {
      this.transitionTo('termsOfService');
    }
  },
  afterModel: function(tasks, transition) {
    if (tasks.get('length') === 0) {
      this.transitionTo('getting_started');
    } else if (transition.targetName == "tasks.index") {
      if($(document).width() > 700) {
        this.transitionTo('task', tasks.get('firstObject'));
      } else {
        if (window.navigator.standalone || window.navigator.userAgent.indexOf('iPhone') === -1) {
          this.transitionTo('mobileTasks');
        } else {
          this.transitionTo('addToHomeScreen');
        }
      }
    }
  },
  actions: {
    error: function(reason, tsn) {
      var application = this.controllerFor('application');
      application.get('handleError').bind(application)(reason, tsn);
    }
  }
});

module.exports = route;

},{}],40:[function(require,module,exports){
var view = Ember.View.extend({
});

module.exports = view;

},{}],41:[function(require,module,exports){
var view = Ember.View.extend({
  templateName: 'tasks',
  name: 'completed'
});

module.exports = view;

},{}],42:[function(require,module,exports){
var view = Ember.View.extend({
  templateName: 'task',
  name: 'completedTask'
});

module.exports = view;

},{}],43:[function(require,module,exports){
var view = Ember.View.extend({
  templateName: 'editTask',
});

module.exports = view;

},{}],44:[function(require,module,exports){

App.CreateTaskView = require("./createTask");
App.CompletedView = require("./completed");
App.CompletedTaskView = require("./completedTask");
App.RefreshView = require("./refresh");
App.ApplicationView = require("./application");
App.TasksView = require("./tasks");
App.TasksIndexView = require("./tasks");
App.TaskView = require("./tasks");

},{"./application":40,"./completed":41,"./completedTask":42,"./createTask":43,"./refresh":45,"./tasks":46}],45:[function(require,module,exports){
var view = Ember.View.extend({
  didInsertElement: function(){
    this.controller.transitionToRoute('tasks');
  }
});

module.exports = view;

},{}],46:[function(require,module,exports){
module.exports=require(40)
},{}]},{},[1,2,21,22,27])