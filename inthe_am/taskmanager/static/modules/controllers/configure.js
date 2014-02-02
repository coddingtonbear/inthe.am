var controller = Ember.Controller.extend({
  needs: ['application'],

  submit_taskd: function(data) {
    if (
      data.certificate === false || data.key === false || data.ca === false
    ) {
      self.error_message("An error was encountered while uploading your files")
      return;
    } else if (
      !data.certificate || !data.key || !data.ca
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
      headers: {
        'X-CSRFToken': csrftoken
      },
      data: data,
      success: function(){
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
  },
  success_message: function(message) {
    $("#settings_alerts").append(
      $("<div>", {'data-alert': '', 'class': 'alert-box success radius'}).append(
        message,
        $("<a>", {'href': '#', 'class': 'close'}).html("&times;")
      )
    );
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
          self.success_message("Taskrc settings saved");
        },
        error: function() {
          self.error_message("An error was encountered while saving your taskrc settings.");
        }
      });
    },
    save_taskd: function() {
      var data = {
        'server': document.getElementById('id_server').value,
        'credentials': document.getElementById('id_credentials').value,
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
  }
});

module.exports = controller;
