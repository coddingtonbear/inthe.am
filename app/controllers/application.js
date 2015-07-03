import Ember from "ember";
import DS from "ember-data";
import Task from "../models/task";
import Router from "../router";

var controller = Ember.Controller.extend({
    needs: ['task', 'tasks', 'activity-log', 'configure'],
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

        'alt+f': 'focus_filter',
    },
    urls: {
        login: '/login/google-oauth2/',
        logout: '/logout/',
        about: '/about/',
        generate_new_certificate: '/api/v1/user/generate-new-certificate/',
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
        clear_lock: '/api/v1/task/lock/',
        sync_init: '/api/v1/task/sync-init/',
        revert_to_last_commit: '/api/v1/task/revert/',
        sync: '/api/v1/task/sync/',
        trello_authorization_url: '/api/v1/task/trello/',
        trello_resynchronization_url: '/api/v1/task/trello/resynchronize/',
        trello_reset_url: '/api/v1/task/trello/reset/',
        status_feed: '/status/',
        feed_url: null,
        sms_url: null,
        pebble_card_url: null,
    },
    ajaxRequest: function(params){
        this.showLoading();
        return $.ajax(params).then(function() {
            this.hideLoading();
            return arguments[0];
        }.bind(this), function(){
            this.hideLoading();
            if (arguments[0].responseText) {
                try {
                    var responseJson = JSON.parse(arguments[0].responseText);
                    return responseJson.error_message;
                } catch(e) {
                    return arguments[0].responseText;
                }
            } else {
                return arguments[2];
            }
        }.bind(this));
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
    reportError: function(error) {
        if (typeof(error) === 'object') {
            if (error.stack) {
                // this is a native JS error; yay!
            } else if (error.statusText) {
                error = new Error(error.status + " " + error.statusText);
            } else {
                error = new Error(JSON.stringify(error));
            }
        } else if (typeof(error) === 'string') {
            error = new Error(error);
        }
        if(window.console && window.console.log) {
            window.console.error("Error encountered", error);
        }
        Raven.captureException(error);
    },
    taskUpdateStreamEnabled: function() {
        var enabled = this.get('user.streaming_enabled');
        var compatible = this.get('controllers.configure.taskUpdateStreamCompatible');
        return enabled && compatible;
    }.property(),
    isHomePage: function() {
        return this.get('currentPath') === "about";
    }.property('currentPath'),
    update_user_info: function(sync) {
        var async = !sync;
        return this.ajaxRequest({
            url: this.get('urls.user_status'),
            dataType: 'json',
            async: async
        }).then(function(data){
            this.set('user', data);
            console.logIfDebug("Got user data", data);
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
                Task.reopen(uda_fields);
                Task.reopen({
                    udas: this.get('user').udas
                });
                if(!this.get('user.tos_up_to_date')) {
                    Ember.run.next(
                            this,
                            function(){
                                    this.transitionToRoute('terms-of-service');
                            }
                    );
                }
                this.handlePostLoginRedirects();
            } else {
                Raven.setUser();
                if(window.localStorage) {
                    if(
                        (!window.location.pathname) ||
                        window.location.pathname !== '/'
                    ) {
                        window.localStorage.setItem(
                            'redirect_to',
                            window.location.href
                        );
                    }
                }
                this.transitionToRoute('about');
            }
            this.set('urls.feed_url', this.get('user').feed_url);
            this.set('urls.sms_url', this.get('user').sms_url);
            this.set('urls.pebble_card_url', this.get('user').pebble_card_url);
            this.set('statusUpdaterHead', this.get('user').repository_head);
        }.bind(this), function(msg){
            this.error_message(
                `An error was encountered while ` +
                `attempting to gather user information: ${msg}`
            );
        }.bind(this));
    },
    handlePostLoginRedirects: function() {
        if(window.localStorage && this.get('user.tos_up_to_date')) {
            var url = window.localStorage.getItem('redirect_to');
            console.logIfDebug("Scheduling redirect", url);
            if(url) {
                Ember.run.later(
                    this,
                    function(){
                        var url = window.localStorage.getItem('redirect_to');
                        console.logIfDebug("Redirecting to", url);
                        window.localStorage.removeItem('redirect_to');
                        if(window.location.pathname.indexOf(url) === -1) {
                            window.location.href = url;
                        }
                    },
                    5000
                );
                return true;
            }
        }
        return false;
    },
    handleError: function(reason) {
        console.logIfDebug("Error encountered", reason);
        if (reason.status === 401) {
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
            if(data.get('length') === 0) {
                Ember.run.next(
                    this,
                    function(){
                        if(this.getHandlerPath() !== "application.fourOhFour") {
                            this.transitionToRoute('getting-started');
                        }
                    }
                );
            }
        }.bind(this), function() {
                this.hideLoading();
        }.bind(this));

        if(window.location.hostname === 'inthe.am') {
            this.set('logo', '/static/logo.png');
            this.set('applicationName', 'Inthe.AM');
        }
        document.title = this.get('applicationName');

        // Set up error reporting
        Ember.onerror = this.reportError;
        Ember.RSVP.configure('onerror', this.reportError);

        // Fetch user information
        this.update_user_info(true);

        this.ajaxRequest({
            url: this.get('urls.announcements'),
            dataType: 'json',
        }).then(function(data){
            $.each(data, function(idx, announcement) {
                $.growl[announcement.type || 'notice']({
                    title: announcement.title || 'Announcement',
                    message: announcement.message || '',
                    duration: announcement.duration || 15000,
                });
            });
        }.bind(this), function(msg){
            this.error_message(
                `An error was encountered while ` +
                `attempting to load announcements: ${msg}`
            );
        }.bind(this));

        // Adding FastClick
        window.addEventListener('load', function() {
            FastClick.attach(document.body);
        }, false);

        // Set up the event stream
        if(this.get('taskUpdateStreamEnabled')) {
            this.set('statusUpdaterLog', []);
            this.startEventStream();
            window.setInterval(this.checkStatusUpdater.bind(this), 500);
        }

        // Set up left-right swipe for returning to the task list
        $("body").touchwipe({
            wipeRight: function() {
                if (self.isSmallScreen()) {
                    self.transitionToRoute('mobile-tasks');
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
                        this.transitionToRoute('add-to-home-screen');
                    }
                );
            }
        }
    },
    taskUpdateStreamStatusMessage: function(){
        var state = this.get('_taskUpdateStreamStatus');
        if (state === 'auto') {
            return 'Connected';
        } else if (state === 'reconnecting') {
            return 'Reconnecting; click to sync tasks';
        } else if (state === 'manual') {
            return 'Sync tasks';
        }
    }.property('_taskUpdateStreamStatus'),
    taskUpdateStreamClass: function(){
        return this.get('_taskUpdateStreamStatus');
    }.property('_taskUpdateStreamStatus'),
    _taskUpdateStreamStatus: function(){
        var enabled = this.get('taskUpdateStreamEnabled');
        var connected = this.get('taskUpdateStreamConnected');
        if(enabled && connected) {
            return 'auto';
        } else if (enabled && !connected) {
            return 'reconnecting';
        } else if (!enabled && !connected) {
            return 'manual';
        }
    }.property('taskUpdateStreamConnected', 'taskUpdateStreamEnabled'),
    checkStatusUpdater: function() {
        var statusUpdater = this.get('statusUpdater');
        var connected = this.get('taskUpdateStreamConnected');
        var now = new Date();
        var lastHeartbeat = this.get('statusUpdaterHeartbeat');
        var flatlineDelay = 19 * 1000; // 19 seconds
        var postDisconnectDelay = 5 * 1000;    // 5 seconds
        if (!statusUpdater) {
            return;
        }
        if (!lastHeartbeat) {
            lastHeartbeat = now;
            this.set('statusUpdaterHeartbeat', lastHeartbeat);
        }
        if (
            (statusUpdater.readyState !== window.EventSource.OPEN) ||
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
            (statusUpdater.readyState === window.EventSource.OPEN) &&
            !connected
        ) {
            this.set('taskUpdateStreamConnected', true);
            this.set('statusUpdaterErrorred', false);
        }
    },
    startEventStream: function() {
        console.logIfDebug("Starting event stream");
        var head = this.get('statusUpdaterHead');
        var log = this.get('statusUpdaterLog');
        this.set('statusUpdaterHeartbeat', new Date());
        log.pushObject(
            [new Date(), 'Starting with HEAD ' + head]
        );
        var statusUpdater = this.get('statusUpdater');
        if (
            this.get('taskUpdateStreamEnabled') &&
            (!statusUpdater || statusUpdater.readyState === window.EventSource.CLOSED)
        ){
            var url = this.get('urls.status_feed');
            if(head && typeof(head) === 'string') {
                url = url + "?head=" +    head;
            }
            statusUpdater = new window.EventSource(url);
            this.bindStatusActions(statusUpdater);
            this.set('statusUpdater', statusUpdater);
            this.set('statusUpdaterHead', head);
        } else {
            this.set('taskUpdateStreamConnected', false);
        }
    },
    eventStreamError: function() {
        this.get('startEventStream').bind(this)();
    },
    updateColorscheme: function() {
        var scheme = this.get('user').colorscheme;
        if(scheme) {
            $("#colorscheme").attr('href', '/colorschemes/' + scheme + '.css');
        }
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
            console.logIfDebug(evt.type, evt.data);
            Ember.run.once(this, function(){
                if (this.store.hasRecordForId('task', evt.data)) {
                    this.store.find('task', evt.data).then(function(record){
                        if (record.get('isLoaded') && (!record.get('isDirty') && !record.get('isSaving'))) {
                            record.reload();
                        }
                    });
                } else {
                    this.store.find('task', evt.data);
                }
            });
        },
        'head_changed': function(evt) {
            console.logIfDebug(evt.type, evt.data);
            this.set('statusUpdaterHead', evt.data);
            try {
                this.store.find('activity-log').update();
            } catch(e) {
                // Pass
            }
        },
        'error_logged': function(evt) {
            console.logIfDebug(evt.type, evt.data);
            $.growl.error({
                title: 'Error',
                message: evt.data
            });
        },
        'heartbeat': function(evt) {
            this.set('statusUpdaterHeartbeat', new Date());
            var heartbeat_data = JSON.parse(evt.data);
            this.set('user.sync_enabled', heartbeat_data.sync_enabled);
        },
        'public_announcement': function(evt) {
          console.logIfDebug(evt.type, evt.data);
        },
        'personal_announcement': function(evt) {
          console.logIfDebug(evt.type, evt.data);
        }
    },
    isSmallScreen: function() {
        return $(document).width() <= 800;
    },
    getHandlerPath: function() {
        var path_parts = [];
        var handlers = Router.router.currentHandlerInfos;
        for(var i = 0; i < handlers.length; i++) {
                path_parts.push(handlers[i].name);
        }
        return path_parts.join('.');
    },
    bindKeyboardEvents: function() {
        var controller = this;
        for (var keycode in this.shortcuts) {
            if (this.shortcuts.hasOwnProperty(keycode)) {
                var event_name = this.shortcuts[keycode];
                $(document).bind('keydown', keycode, function(name, evt) {
                    evt.stopPropagation();
                    controller.send(name, controller);
                    return false;
                }.bind(this, event_name));
            }
        }
    },
    closeModal: function(node) {
        if(node) {
            node.foundation('reveal', 'close');
            setTimeout(function(){
                $('.reveal-modal').remove();
            }, 1500);
        }
        this.get('target').send('disconnectModalOutlet');
    },
    actions: {
        refresh: function(){
            if (this.get('_taskUpdateStreamStatus') === 'auto') {
                /* Do not do a manual refresh if we're in auto mode. */
                return;
            }
            this.showLoading();
            this.get('controllers.tasks').refresh(function(){
                this.hideLoading();
            }.bind(this), function(){
                this.hideLoading();
            }.bind(this));
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
                );
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
                if(currentBgColor !== targetBgColor) {
                    this.set(
                        '_chardin_original_bgcolor',
                        currentBgColor
                    );
                }
                $('nav').css('background-color', targetBgColor);

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
            this.transitionToRoute('activity-log');
        },
        launch_configuration: function() {
            this.transitionToRoute('configure');
        },
        show_tasks: function(){
            if($(document).width() > 700) {
                this.transitionToRoute('tasks');
            } else {
                this.transitionToRoute('mobile-tasks');
            }
        },
        show_create_task: function() {
            if($(document).width() > 700) {
                this.send('create_task');
            } else {
                this.transitionToRoute('create-task');
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
        },
        focus_filter: function() {
                $('#filter-string').focus();
        },
    }
});

export default controller;
