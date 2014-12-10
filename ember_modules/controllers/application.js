var controller = Ember.Controller.extend({
  needs: ['task', 'tasks', 'activityLog', 'configure'],
  logo: '',
  applicationName: 'Local Installation',
  user: null,
  shortcuts: {
      'alt+h': 'show_help',
      'alt+l': 'show_log',
      'alt+/': 'launch_configuration',
      'alt+x': 'logout',
  
      'alt+t': 'show_tasks',
      'alt+n': 'show_create_task',

      'alt+r': 'refresh',

      'alt+s': 'start_or_stop',
      'alt+a': 'add_annotation',
      'alt+e': 'edit_task',
      'alt+c': 'complete_task',
      'alt+d': 'delete_task',

      'alt+up': 'prev_task',
      'alt+down': 'next_task',
      'alt+left': 'show_tasks',
      'alt+right': 'show_task',
  },
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
    email_integration: '/api/v1/user/email-integration/',
    twilio_integration: '/api/v1/user/twilio-integration/',
    tos_accept: '/api/v1/user/tos-accept/',
    clear_task_data: '/api/v1/user/clear-task-data/',
    set_colorscheme: '/api/v1/user/colorscheme/',
    enable_sync: '/api/v1/user/enable-sync/',
    mirakel_configuration: '/api/v1/user/mirakel-configuration/',
    configure_pebble_cards: '/api/v1/user/pebble-cards-config/',
    configure_feed: '/api/v1/user/feed-config/',
    user_status: '/api/v1/user/status/',
    announcements: '/api/v1/user/announcements/',
    refresh: '/api/v1/task/refresh/',
    sync_init: '/api/v1/task/sync-init/',
    status_feed: '/status/',
    feed_url: null,
    sms_url: null,
    pebble_card_url: null,
  },
  showLoading: function() {
    $('#loading').show();
  },
  hideLoading: function() {
    Ember.run.next(this, '_hideLoading');
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
  _hideLoading: function() {
    $('#loading').hide();
  },
  taskUpdateStreamEnabled: function() {
    return this.get('controllers.configure.taskUpdateStreamEnabled');
  }.property(),
  isHomePage: function() {
    return this.get('currentPath') == "about";
  }.property('currentPath'),
  update_user_info: function() {
    this.set(
      'user',
      JSON.parse(
        $.ajax(
          {
            url: this.get('urls.user_status'),
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
      // Re-open the model class to append the known UDAs
      var uda_fields = {};
      for(var i = 0; i < this.get('user').udas.length; i++) {
        var this_uda = this.get('user').udas[i];
        var attr_type = 'string';
        if(this_uda.type === 'DateField') {
          attr_type = 'date';
        } else if(this_uda.type === 'NumericField') {
          attr_type = 'number';
        }
        uda_fields[this_uda.field] = DS.attr(attr_type);
      }
      App.Task.reopen(uda_fields);
      App.Task.reopen({
        udas: this.get('user').udas
      });

      if(!this.get('user.tos_up_to_date')) {
        Ember.run.next(
            this,
            function(){
                this.transitionToRoute('termsOfService');
            }
        );
      }
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
    // Load all tasks; the views are all populated by promises
    // so whenever this is fulfilled, they'll automatically be populated
    this.showLoading();
    this.store.find('task').then(function(data) {
        this.hideLoading();
        if(data.get('length') == 0) {
            Ember.run.next(
                this,
                function(){
                    if(this.getHandlerPath() != "application.fourOhFour") {
                        this.transitionToRoute('getting_started');
                    }
                }
            );
        }
    }.bind(this), function() {
        this.hideLoading();
    }.bind(this));;

    if(window.location.hostname == 'inthe.am') {
        this.set('logo', '/static/logo.png');
        this.set('applicationName', 'Inthe.AM');
    }
    document.title = this.get('applicationName');

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
    $.ajax({
      url: this.get('urls.announcements'),
      dataType: 'json',
      success: function(data) {
        $.each(data, function(idx, announcement) {
          $.growl[announcement.type || 'notice']({
            title: announcement.title || 'Announcement',
            message: announcement.message || '',
            duration: announcement.duration || 15000,
          });
        });
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

    // Set up left-right swipe for returning to the task list
    $("body").touchwipe({
      wipeRight: function() {
        if (self.isSmallScreen()) {
          self.transitionToRoute('mobileTasks');
        }
      },
      min_move_x: 100,
      preventDefaultEvents: false
    });

    // If the user is on a small screen:
    if($(document).width() <= 700) {
      if (!(window.navigator.standalone || window.navigator.userAgent.indexOf('iPhone') === -1)) {
        Ember.run.next(
          this,
          function(){
            this.transitionToRoute('addToHomeScreen');
          }
        );
      }
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
        if (this.store.hasRecordForId('task', evt.data)) {
          this.store.find('task', evt.data).then(function(record){
            if (record.get('isLoaded') && (!record.get('isDirty') && !record.get('isSaving'))) {
              record.reload();
            }
          });
        } else {
          this.store.find('task', evt.data)
        }
      });
    },
    'head_changed': function(evt) {
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
  getHandlerPath: function() {
      var path_parts = [];
      var handlers = App.Router.router.currentHandlerInfos;
      for(var i = 0; i < handlers.length; i++) {
          path_parts.push(handlers[i].name);
      }
      return path_parts.join('.');
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
  bindKeyboardEvents: function() {
    var controller = this;
    for (var keycode in this.shortcuts) {
      if (this.shortcuts.hasOwnProperty(keycode)) {
        var event_name = this.shortcuts[keycode];
        $(document).on('keydown', null, keycode, function(name, evt) {
          controller.send(name, controller);
        }.bind(this, event_name));
      }
    }
  },
  actions: {
    refresh: function(){
      this.get('controllers.tasks').refresh();
    },
    home: function(){
      window.location = '/';
    },
    login: function(){
      window.location = this.get('urls.login');
    },
    logout: function(){
      window.location = this.get('urls.logout');
    },
    _help_hidden: function() {
      // Re-set navigation bar background color
      var originalBgColor = this.get('_chardin_original_bgcolor');
      if(originalBgColor) {
        $('nav').css(
          'background-color',
          originalBgColor
        )
      }

      // Hide addenda
      $('.chardinjs-addenda').fadeOut();
    },
    show_help: function(){
      // ALSO: see `_help_hidden` for cleanup when chardin closes.
      if($('.chardinjs-overlay').length) {
        // Hide overlay
        $('body').chardinJs('stop');
      } else {
        // Show overlay
        $('body').chardinJs('start');

        // Set navigation bar background color
        var currentBgColor = $('nav').css('background-color');
        var targetBgColor = '#000';
        if(currentBgColor != targetBgColor) {
          this.set(
            '_chardin_original_bgcolor',
            currentBgColor
          );
        }
        $('nav').css('background-color', targetBgColor)

        // Show corner help information
        var helpInstructionsView = Ember.View.create({
          template: this.container.lookup(
            'template:helpInstructions'
          )
        });
        helpInstructionsView.appendTo(
          $('.chardinjs-overlay')
        );
      }
    },
    show_log: function() {
      this.transitionToRoute('activityLog');
    },
    launch_configuration: function() {
      this.transitionToRoute('configure');
    },
    show_tasks: function(){
      if($(document).width() > 700) {
        this.transitionToRoute('tasks');
      } else {
        this.transitionToRoute('mobileTasks');
      }
    },
    show_create_task: function() {
      if($(document).width() > 700) {
        this.send('create_task');
      } else {
        this.transitionToRoute('createTask');
      }
    },
    start_or_stop: function() {
      var taskController = this.get('controllers.task');
      var model = taskController.get('model');
      if(model.get('start')) {
        taskController.send('stop');
      } else {
        taskController.send('start');
      }
    },
    add_annotation: function() {
      var taskController = this.get('controllers.task');
      taskController.send('add_annotation');
    },
    edit_task: function() {
      var taskController = this.get('controllers.task');
      taskController.send('edit');
    },
    complete_task: function() {
      var taskController = this.get('controllers.task');
      taskController.send('complete');
    },
    delete_task: function() {
      var taskController = this.get('controllers.task');
      taskController.send('delete');
    },
    prev_task: function() {
      var tasksController = this.get('controllers.tasks');
      tasksController.send('prev_task');
    },
    next_task: function() {
      var tasksController = this.get('controllers.tasks');
      tasksController.send('next_task');
    },
    show_task: function() {
        var taskController = this.get('controllers.task');
        var task = taskController.get('model');
        if(task) {
            this.transitionToRoute('task', task);
        }
    }
  }
});

module.exports = controller;
