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
    ajaxRequest: function(params) {
        return this.get('applicationController').ajaxRequest(params);
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
        save_taskd_and_init: function() {
            var self = this;
            this.send(
                'save_taskd',
                function() {
                    self.sync_with_init();
                }
            );
        },
        save_taskd: function(after) {
            var data = {
                server: document.getElementById('id_server').value,
                credentials: document.getElementById('id_credentials').value,
                trust: document.getElementById('id_trust').value,
            };
            var self = this;

            // Load Cert
            var cert_reader = new window.FileReader();
            cert_reader.onload = function(evt){
                data.certificate = evt.target.result;
                self.submit_taskd(data, after);
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
            try {
                cert_reader.readAsBinaryString(cert_file);
            } catch(e) {
                self.error_message("An error was encountered while reading your certificate.");
            }

            // Load Key
            var key_reader = new window.FileReader();
            key_reader.onload = function(evt){
                data.key = evt.target.result;
                self.submit_taskd(data, after);
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
            try {
                key_reader.readAsBinaryString(key_file);
            } catch(e) {
                self.error_message("An error was encountered while reading your key.");
            }

            // Load CA Certificate
            if (data.trust === 'no') {
                var ca_reader = new window.FileReader();
                ca_reader.onload = function(evt){
                    data.ca = evt.target.result;
                    self.submit_taskd(data, after);
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
                try {
                    ca_reader.readAsBinaryString(ca_file);
                }catch(e) {
                    self.error_message("An error was encountered while reading your CA Certificate.");
                }
            }
        },
        save_email: function() {
            var data = {
                'email_whitelist': document.getElementById('id_email_whitelist').value,
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
                'twilio_auth_token': document.getElementById('id_twilio_auth_token').value,
                'sms_whitelist': document.getElementById('id_sms_whitelist').value,
                'sms_arguments': document.getElementById('id_sms_arguments').value,
                'sms_replies': document.getElementById('id_sms_replies').value,
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
            var value = $('#id_theme').val();
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
            } else if($("#id_ical_config").val() === "true") {
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
            } else if($("#id_feed_config").val() === "true") {
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
            else if($("#id_pebble_cards_config").val() === "true") {
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
            var data = document.getElementById('id_bugwarrior_config').value;
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
                  )
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to request a bugwarrior synchronization: ${msg}`
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
