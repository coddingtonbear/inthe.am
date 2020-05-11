import Ember from 'ember'
import ObjectController from 'ember-legacy-controllers/object'

var controller = ObjectController.extend({
  applicationController: Ember.inject.controller('application'),
  priorities: [
        {short: '', long: '(none)'},
        {short: 'L', long: 'Low'},
        {short: 'M', long: 'Medium'},
        {short: 'H', long: 'High'}
  ],
  actions: {
    'save': function () {
      var model = this.get('model')
      var application = this.get('applicationController')
      var self = this
      application.showLoading()
      model.save().then(function () {
        application.closeModal($('#new_task_form'))
        application.hideLoading()
        self.transitionToRoute('task', model)
      }, function (reason) {
        model.rollbackAttributes()
        model.reload()
        application.hideLoading()
        application.error_message(
                    'An error was encountered while ' +
                    'saving this task.  Check your ' +
                    'Activity Log for more information.'
                )
        application.get('handleError').bind(application)(reason)
      })
    }
  }
})

export default controller
