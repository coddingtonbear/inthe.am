import Ember from "ember";

var controller = Ember.Controller.extend({
    applicationController: Ember.inject.controller('application'),
    taskd_trust_settings: [
        {short: 'no', long: 'Validate taskserver using an uploaded CA Certificate'},
        {short: 'yes', long: 'Trust taskserver implicitly; do not validate using a CA Certificate'},
    ],
    taskUpdateStringSettings: [
        {short: 'no', long: 'Disabled'},
        {short: 'yes', long: 'Enabled'},
    ],
    smsRepliesSettings: [
        {short: 0, long: 'Do not reply to any incoming text messages'},
        {short: 5, long: 'Reply only when an error has occurred'},
        {short: 9, long: 'Reply to all messages'},
    ],
    taskd_server_settings: [
        {value: true, human: "Use the built-in taskserver"},
        {value: false, human: "Use a custom taskserver"},
    ],
    pebbleCardsEnabledUI: [
        {value: false, human: 'Disabled'},
        {value: true, human: 'Enabled'},
    ],
    feedEnabledUI: [
        {value: false, human: 'Disabled'},
        {value: true, human: 'Enabled'},
    ],
    deduplicateUI: [
        {value: false, human: 'No'},
        {value: true, human: 'Yes'},
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
    taskUpdateStreamCompatible: function() {
        if(!window.EventSource) {
            return false;
        }
        return true;
    }.property(),
    ajaxRequest: function(params, returnAll) {
        return this.get('applicationController').ajaxRequest(params, returnAll);
    },
    sync_with_init: function() {
        var url = this.get('applicationController').urls.sync_init;

        return this.ajaxRequest({
            url: url,
            type: 'POST',
        }).then(function(){
            this.get('applicationController').update_user_info();
            this.success_message(
                "Initial sync completed successfully."
            );
        }.bind(this), function(msg){
            this.error_message(
                `An error was encountered while ` +
                `attempting to complete initial synchronization: ${msg}`
            );
        }.bind(this));
    },
    submit_taskd: function(data, after) {
        if (
            data.certificate === false || data.key === false || data.ca === false
        ) {
            self.error_message("An error was encountered while uploading your files");
            return;
        } else if (
            !data.certificate || !data.key || (!data.ca && data.trust === 'no')
        ) {
            return;
        }
        var url = this.get('applicationController').urls.taskd_settings;
        var self = this;

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            success: function(){
                self.get('applicationController').update_user_info();
                self.success_message("Taskserver settings saved.");
                if(after) {
                    after();
                }
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
        this.get('applicationController').error_message(message);
    },
    success_message: function(message) {
        this.get('applicationController').success_message(message);
    },
    growl_message: function(type, opts) {
        $.growl[type || 'notice'](opts || {});
    },
    actions: {
        save_taskrc: function() {
            var url = this.get('applicationController').urls.taskrc_extras;
            var value = $('textarea[name=custom_taskrc]').val();
            return this.ajaxRequest({
                url: url,
                type: 'PUT',
                dataType: 'text',
                data: value
            }).then(function(response) {
                this.get('applicationController').update_user_info();
                this.success_message("Taskrc settings saved");
            }.bind(this), function(msg) {
                this.error_message(
                    `An error was encountered while ` +
                    `saving your taskrc settings: ${msg}.`
                );
            }.bind(this));
        },
        get_file_from_url: function(url, filename) {
            return this.ajaxRequest({
                url: url,
                type: 'GET',
                data: {}
            }, true).then(function(data){
                var xhr = data[2];
                var data = data[0];
                var element = document.createElement('a');
                element.setAttribute(
                    'href',
                    'data:' +
                    xhr.getResponseHeader('Content-Type') +
                    'charset=utf-8,' +
                    encodeURIComponent(data)
                );
                element.setAttribute(
                    'download',
                    filename
                );
                element.style.display = 'none';
                document.body.appendChild(element);
                element.click();

                document.body.removeChild(element);
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `downloading your certificate: ${msg}`
                );
            }.bind(this));
        },
        regenerate_taskd_certificate: function() {
            var url = this.get('applicationController').urls.generate_new_certificate;
            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {}
            }).then(function(){
                this.get('applicationController').update_user_info();
                this.success_message("New taskserver certificate generated!");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `regenerating your taskserver certificate: ${msg}`
                );
            }.bind(this));
        },
        trello_force_resynchronization: function() {
            var url = this.get('applicationController').urls.trello_resynchronization_url;
            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {}
            }).then(function(){
                this.success_message(
                  "Trello resynchronization requested.  It may take a few minutes before " +
                  "you see any results."
                );
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `requesting a resynchronization with Trello: ${msg}`
                );
            }.bind(this));
        },
        reset_trello_settings: function() {
            var url = this.get('applicationController').urls.trello_reset_url;
            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {}
            }).then(function(){
                this.get('applicationController').update_user_info();
                this.success_message("Trello settings successfully reset.");
                setTimeout(function(){
                    window.location.reload();
                }, 3000);
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `resetting your trello settings: ${msg}`
                );
            }.bind(this));
        },
        reset_taskd: function() {
            var result = confirm(
                `Are you sure you would like to configure your Inthe.AM ` +
                `task list to synchronize with the built-in taskserver ` +
                `rather than a custom one?`
            );
            if(!result) {
                return;
            }
            var url = this.get('applicationController').urls.taskd_reset;
            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {}
            }).then(function(){
                this.get('applicationController').update_user_info();
                this.success_message("Taskserver settings reset to default.");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `resetting your taskserver settings ` +
                    `to their defaults: ${msg}`
                );
            }.bind(this));
        },
        save_email: function() {
            var value = $('textarea[name=email_whitelist]').val();
            var data = {
                'email_whitelist': value,
            };
            var url = this.get('applicationController').urls.email_integration;

            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: data,
            }).then(function(){
                this.success_message("Email settings saved.");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `updating your e-mail whitelist: ${msg}`
                );
            }.bind(this));
        },
        save_twilio: function() {
            var data = {
                'twilio_auth_token': $('input[name=twilio_auth_token]').val(),
                'sms_whitelist': $('textarea[name=sms_whitelist]').val(),
                'sms_arguments': $('input[name=sms_arguments]').val(),
                'sms_replies': $('select[name=sms_replies]').val()
            };
            var url    = this.get('applicationController').urls.twilio_integration;

            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: data
            }).then(function(){
                this.success_message("Twilio settings saved.");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `updating your twilio configuration: ${msg}`
                );
            }.bind(this));
        },
        clear_task_data: function() {
            var url    = this.get('applicationController').urls.clear_task_data;

            return this.ajaxRequest({
                url: url,
                type: 'POST'
            }).then(function(){
                this.success_message("Task data cleared");
                setTimeout(function(){
                    window.location.reload();
                }, 3000);
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to clear your task data: ${msg}`
                );
            }.bind(this));
        },
        clear_lock: function() {
            var url    = this.get('applicationController').urls.clear_lock;

            return this.ajaxRequest({
                url: url,
                type: 'DELETE',
            }).then(function(){
                this.success_message("Task list unlocked.");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to unlock your task list repository: ${msg}`
                );
            }.bind(this));
        },
        save_colorscheme: function() {
            var value = $('select[name=theme_selector]').val();
            var url    = this.get('applicationController').urls.set_colorscheme;

            return this.ajaxRequest({
                url: url,
                type: 'PUT',
                data: value,
            }).then(function(){
                this.set('applicationController.user.colorscheme', value);
                this.get('applicationController').updateColorscheme();
                this.success_message("Colorscheme saved!");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to set your colorscheme: ${msg}`
                );
            }.bind(this));
        },
        save_ical: function(value) {
            var url = this.get('applicationController').urls.configure_ical;
            var enabled = false;
            if(typeof(value) !== 'undefined') {
                enabled = value;
            } else if($("select[name=ical_config]").val() === "true") {
                enabled = true;
            }
            
            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {
                    enabled: enabled ? 1 : 0,
                },
            }).then(function(){
                this.set('applicationController.user.ical_enabled', enabled);
                if(enabled) {
                    this.success_message("iCal feed enabled!");
                } else {
                    this.success_message("iCal feed disabled!");
                }
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to configure your feed settings: ${msg}`
                );
            }.bind(this));
        },
        save_feed: function(value) {
            var url = this.get('applicationController').urls.configure_feed;
            var enabled = false;
            if(typeof(value) !== 'undefined') {
                enabled = value;
            } else if($("select[name=feed_config]").val() === "true") {
                enabled = true;
            }
            
            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {
                    enabled: enabled ? 1 : 0,
                },
            }).then(function(){
                this.set('applicationController.user.feed_enabled', enabled);
                if(enabled) {
                    this.success_message("Feed enabled!");
                } else {
                    this.success_message("Feed disabled!");
                }
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to configure your feed settings: ${msg}`
                );
            }.bind(this));
        },
        save_pebble_cards: function(value) {
            var url    = this.get('applicationController').urls.configure_pebble_cards;
            var enabled = false;
            if(typeof(value) !== 'undefined') {
                enabled = value;
            }
            else if($("select[name=pebble_cards_config]").val() === "true") {
                enabled = true;
            }

            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {
                    enabled: enabled ? 1 : 0,
                },
            }).then(function(){
                this.set('applicationController.user.pebble_cards_enabled', enabled);
                if(enabled) {
                    this.success_message("Pebble Cards URL enabled!");
                } else {
                    this.success_message("Pebble Cards URL disabled!");
                }
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to configure pebble cards: ${msg}`
                );
            }.bind(this));
        },
        enable_sync: function() {
            var url = this.get('applicationController').urls.enable_sync;

            return this.ajaxRequest({
                url: url,
                type: 'POST',
            }).then(function(){
                this.set('applicationController.user.sync_enabled', true);
                this.success_message("Sync re-enabled!");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to enable sync: ${msg}`
                );
            }.bind(this));
        },
        update_bugwarrior_config: function() {
            var url = this.get('applicationController').urls.bugwarrior_config;
            var data = $('textarea[name=bugwarrior_config]').val();
            return this.ajaxRequest({
                url: url,
                type: 'PUT',
                data: data,
            }).then(function(){
                this.success_message("Bugwarrior configuration updated.");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to updating your bugwarrior configuration: ${msg}`
                );
            }.bind(this));
        },
        delete_bugwarrior_configuration: function() {
            var url = this.get('applicationController').urls.bugwarrior_config;
            return this.ajaxRequest({
                url: url,
                type: 'DELETE',
            }).then(function(){
                this.set('applicationController.user.bugwarrior_configured', false);
                this.success_message("Bugwarrior configuration deleted");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to delete your bugwarrior configuration: ${msg}`
                );
            }.bind(this));
        },
        schedule_bugwarrior_synchronization: function() {
            var url = this.get('applicationController').urls.bugwarrior_sync;
            return this.ajaxRequest({
                url: url,
                type: 'POST',
            }).then(function(){
                this.success_message(
                    `Bugwarrior synchronization requested; it may take a ` +
                    `few minutes for the synchronization to take place.`
                  );
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to request a bugwarrior synchronization: ${msg}`
                );
            }.bind(this));
        },
        deduplicate_tasks: function() {
            var url = this.get('applicationController').urls.deduplicate_tasks;
            return this.ajaxRequest({
                url: url,
                type: 'POST',
            }).then(function(){
                this.success_message(
                    `Task de-duplication requested;  it may take a few ` +
                    `minutes for the de-duplicate to take place.`
                  );
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to request task de-duplication: ${msg}`
                );
            }.bind(this));
        },
        revert_to_last_commit: function(){
            var url = this.get('applicationController').urls.revert_to_last_commit;

            return this.ajaxRequest({
                url: url,
                type: 'POST'
            }).then(function(data){
                this.success_message(
                    `Your task list was successfully reverted to ` + 
                    `an earlier state (${data.old_head} to ${data.new_head}).`
                );
                setTimeout(function(){
                    window.location.reload();
                }, 3000);
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to revert your task list ` +
                    `to its earlier state: ${msg}`
                );
            }.bind(this));
        }
    }
});

export default controller;
