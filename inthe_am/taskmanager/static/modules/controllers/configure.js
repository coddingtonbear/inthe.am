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
    $("#settings_alerts").append(
      $("<div>", {'data-alert': '', 'class': 'alert-box error radius'}).append(
        message,
        $("<a>", {'href': '#', 'class': 'close'}).html("&times;")
      )
    );
    var reloadFoundation = function(){
      $(document).foundation();
    };
    Ember.run.scheduleOnce('afterRender', this, reloadFoundation);
  },
  success_message: function(message) {
    $("#settings_alerts").append(
      $("<div>", {'data-alert': '', 'class': 'alert-box success radius'}).append(
        message,
        $("<a>", {'href': '#', 'class': 'close'}).html("&times;")
      )
    );
    var reloadFoundation = function(){
      $(document).foundation();
    };
    Ember.run.scheduleOnce('afterRender', this, reloadFoundation);
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
    }
  }
});

module.exports = controller;
