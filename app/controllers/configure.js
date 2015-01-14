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
    sync_with_init: function() {
        var url = this.get('controllers.application').urls.sync_init;
        var self = this;
        $.ajax({
            url: url,
            type: 'POST',
            success: function(){
                self.get('controllers.application').update_user_info();
                self.success_message(
                        "Initial sync completed successfully."
                );
            },
            error: function(xhr){
                self.error_message(
                    "Error encountered while completing initial sync."
                );
            }
        });
    },
    submit_taskd: function(data, after) {
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
        $.growl[type || 'notice'](opts || {})
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
        regenerate_taskd_certificate: function() {
            var url = this.get('controllers.application').urls.generate_new_certificate;
            var self = this;
            $.ajax({
                url: url,
                type: 'POST',
                data: {},
                success: function(){
                    self.get('controllers.application').update_user_info();
                    self.success_message("New taskserver certificate generated!");
                },
                error: function(xhr){
                    self.error_message(
                        "Error encountered while generating taskserver certificate!"
                    );
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
                    self.success_message("Taskserver settings reset to default.");
                },
                error: function(xhr){
                    self.error_message(
                        "Error encountered while resetting taskserver settings to defaults."
                    );
                }
            });
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
            var cert_reader = new FileReader();
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
            var key_reader = new FileReader();
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
                var ca_reader = new FileReader();
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
            }
            var url    = this.get('controllers.application').urls.email_integration;
            var self = this;

            $.ajax({
                url: url,
                type: 'POST',
                data: data,
                success: function() {
                    self.success_message("Email settings saved.");
                },
                error: function(xhr) {
                    var response = JSON.parse(xhr.responseText);
                    for (var property in response) {
                        self.error_message(
                            "Error encountered: " + property + ": " + response[property]
                        );
                    }
                }
            });
        },
        save_twilio: function() {
            var data = {
                'twilio_auth_token': document.getElementById('id_twilio_auth_token').value,
                'sms_whitelist': document.getElementById('id_sms_whitelist').value
            };
            var url    = this.get('controllers.application').urls.twilio_integration;
            var self = this;

            $.ajax({
                url: url,
                type: 'POST',
                data: data,
                success: function() {
                    self.success_message("Twilio settings saved.");
                },
                error: function(xhr) {
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
            var url    = this.get('controllers.application').urls.clear_task_data;
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
                error: function(xhr) {
                    var response = JSON.parse(xhr.responseText);
                    for (var property in response) {
                        self.error_message(
                            "Error encountered: " + property + ": " + response[property]
                        );
                    }
                }
            });
        },
        clear_lock: function() {
            var url    = this.get('controllers.application').urls.clear_lock;
            var self = this;

            $.ajax({
                url: url,
                type: 'DELETE',
                success: function() {
                    self.success_message("Task list unlocked.");
                },
                error: function(xhr) {
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
            var url    = this.get('controllers.application').urls.set_colorscheme;
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
            var url    = this.get('controllers.application').urls.configure_feed;
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
            var url    = this.get('controllers.application').urls.configure_pebble_cards;
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
            var url    = this.get('controllers.application').urls.enable_sync;
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

export default controller;
