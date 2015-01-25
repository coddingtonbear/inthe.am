import Ember from "ember";

var controller = Ember.Controller.extend({
    needs: ['application'],
    taskd_trust_settings: [
        {short: 'no', long: 'Validate taskserver using an uploaded CA Certificate'},
        {short: 'yes', long: 'Trust taskserver implicitly; do not validate using a CA Certificate'},
    ],
    taskUpdateStringSettings: [
        {short: 'no', long: 'Disabled'},
        {short: 'yes', long: 'Enabled'},
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
    taskUpdateStreamEnabledUI: function() {
        if(this.get('taskUpdateStreamEnabled')) {
            return 'yes';
        } else {
            return 'no';
        }
    }.property(),
    taskUpdateStreamEnabled: function() {
        var enabled = this.get('controllers.application.user.streaming_enabled');
        if(!this.get('taskUpdateStreamCompatible')) {
            return false;
        }
        if(!enabled) {
            return false;
        }
        return true;
    }.property(),
    taskUpdateStreamCompatible: function() {
        if(!window.EventSource) {
            return false;
        }
        return true;
    }.property(),
    ajaxRequest: function(params) {
        return this.get('controllers.application').ajaxRequest(params);
    },
    sync_with_init: function() {
        var url = this.get('controllers.application').urls.sync_init;

        return this.ajaxRequest({
            url: url,
            type: 'POST',
        }).then(function(){
            this.get('controllers.application').update_user_info();
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
        var url = this.get('controllers.application').urls.taskd_settings;
        var self = this;

        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            success: function(){
                self.get('controllers.application').update_user_info();
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
        this.get('controllers.application').error_message(message);
    },
    success_message: function(message) {
        this.get('controllers.application').success_message(message);
    },
    growl_message: function(type, opts) {
        $.growl[type || 'notice'](opts || {});
    },
    actions: {
        save_taskrc: function() {
            var url = this.get('controllers.application').urls.taskrc_extras;
            var value = $('textarea[name=custom_taskrc]').val();
            return this.ajaxRequest({
                url: url,
                type: 'PUT',
                dataType: 'text',
                data: value
            }).then(function(response) {
                this.get('controllers.application').update_user_info();
                this.success_message("Taskrc settings saved");
            }.bind(this), function(msg) {
                this.error_message(
                    `An error was encountered while ` +
                    `saving your taskrc settings: ${msg}.`
                );
            }.bind(this));
        },
        regenerate_taskd_certificate: function() {
            var url = this.get('controllers.application').urls.generate_new_certificate;
            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {}
            }).then(function(){
                this.get('controllers.application').update_user_info();
                this.success_message("New taskserver certificate generated!");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `regenerating your taskserver certificate: ${msg}`
                );
            }.bind(this));
        },
        reset_taskd: function() {
            var url = this.get('controllers.application').urls.taskd_reset;
            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {}
            }).then(function(){
                this.get('controllers.application').update_user_info();
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
            var url = this.get('controllers.application').urls.email_integration;

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
                'sms_whitelist': document.getElementById('id_sms_whitelist').value
            };
            var url    = this.get('controllers.application').urls.twilio_integration;

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
        save_streaming: function() {
            var url = this.get('controllers.application').urls.configure_streaming;
            var value = 0;

            if($("#id_update_stream").val() !== 'no') {
                value = 1;
            }
            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {
                    enabled: value ? 1 : 0,
                },
            }).then(function(){
                if (value) {
                    this.success_message("Streaming ticket updates enabled.");
                } else {
                    this.success_message("Streaming ticket updates disabled.");
                }
                setTimeout(function(){
                    window.location.reload();
                }, 3000);
            }.bind(this), function(msg) {
                this.error_message(
                    `An error was encountered while ` +
                    `configuring streaming updates: ${msg}`
                );
                setTimeout(function(){
                    window.location.reload();
                }, 3000);
            }.bind(this));
        },
        clear_task_data: function() {
            var url    = this.get('controllers.application').urls.clear_task_data;

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
            var url    = this.get('controllers.application').urls.clear_lock;

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
            var url    = this.get('controllers.application').urls.set_colorscheme;

            return this.ajaxRequest({
                url: url,
                type: 'PUT',
                data: value,
            }).then(function(){
                this.set('controllers.application.user.colorscheme', value);
                this.get('controllers.application').updateColorscheme();
                this.success_message("Colorscheme saved!");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to set your colorscheme: ${msg}`
                );
            }.bind(this));
        },
        save_feed: function(value) {
            var url = this.get('controllers.application').urls.configure_feed;
            var enabled = false;
            if(typeof(value) !== 'undefined') {
                enabled = value;
            } else if($("#id_feed_config").val() === true) {
                enabled = true;
            }
            
            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {
                    enabled: enabled ? 1 : 0,
                },
            }).then(function(){
                this.set('controllers.application.user.feed_enabled', enabled);
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
            var url    = this.get('controllers.application').urls.configure_pebble_cards;
            var enabled = false;
            if(typeof(value) !== 'undefined') {
                enabled = value;
            }
            else if($("#id_pebble_cards_config").val() === true) {
                enabled = true;
            }

            return this.ajaxRequest({
                url: url,
                type: 'POST',
                data: {
                    enabled: enabled ? 1 : 0,
                },
            }).then(function(){
                this.set('controllers.application.user.pebble_cards_enabled', enabled);
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
            var url    = this.get('controllers.application').urls.enable_sync;

            return this.ajaxRequest({
                url: url,
                type: 'POST',
            }).then(function(){
                this.set('controllers.application.user.sync_enabled', true);
                this.success_message("Sync re-enabled!");
            }.bind(this), function(msg){
                this.error_message(
                    `An error was encountered while ` +
                    `attempting to enable sync: ${msg}`
                );
            }.bind(this));
        }
    }
});

export default controller;
