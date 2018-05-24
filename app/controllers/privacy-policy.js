import Ember from 'ember'

var controller = Ember.Controller.extend({
  applicationController: Ember.inject.controller('application'),
  mustAccept: Ember.computed(
    'applicationController.user',
    function () {
      let appCtrl = this.get('applicationController')
      return (
        appCtrl.get('user.logged_in') &&
        !appCtrl.get('user.privacy_policy_up_to_date')
      )
    }
  ),
  actions: {
    accept: function (version) {
      return this.get('applicationController').ajaxRequest({
        url: this.get('applicationController').urls.privacy_policy_accept,
        type: 'POST',
        data: {
          version: version
        }
      }).then(function () {
        this.get('applicationController').update_user_info()
        this.get('applicationController').handlePostLoginRedirects()
        this.transitionToRoute('getting-started')
      }.bind(this), function (msg) {
        this.get('applicationController').error_message(
                    `An error was encountered while ` +
                    `attempting to accept the privacy policy: ${msg}`
                )
      }.bind(this))
    }
  }
})

export default controller
