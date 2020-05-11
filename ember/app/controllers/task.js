import Ember from 'ember'
import ObjectController from 'ember-legacy-controllers/object'

var controller = ObjectController.extend({
  applicationController: Ember.inject.controller('application'),
  tasksController: Ember.inject.controller('tasks'),
  ajaxRequest: function (params) {
    return this.get('applicationController').ajaxRequest(params)
  },
  udaList: Ember.computed('udas', 'applicationController.user', function () {
    var fieldNameMap = {}
    var userUdas = this.get('applicationController.user.udas')
    for (var udaIdx in userUdas) {
      var uda = userUdas[udaIdx]
      fieldNameMap[uda.field] = {
        'label': uda.label,
        'type': uda['type']
      }
    }

    var udas = []
    var modelUdas = this.get('model.udas')
    for (var defined_uda in modelUdas) {
      if (fieldNameMap[defined_uda]) {
        udas.push({
          'field_name': defined_uda,
          'value': modelUdas[defined_uda],
          'label': fieldNameMap[defined_uda].label,
          'type': fieldNameMap[defined_uda]['type']
        })
      }
    }

    return udas
  }),
  actions: {
    'complete': function () {
      var result = confirm('Are you sure you would like to mark this task as completed?')
      if (result) {
        var self = this
        this.get('applicationController').showLoading()
        this.get('model').destroyRecord().then(function () {
          self.get('applicationController').hideLoading()
          self.transitionToRoute('tasks')
        }, function () {
          self.get('applicationController').hideLoading()
          self.get('applicationController').error_message(
                            'Could not complete task!'
                    )
        })
      }
    },
    'delete_annotation': function (rawDescription) {
      var model = this.get('model')
      var self = this
      var annotations = model.get('annotations')
      this.get('applicationController').showLoading()

            // Sometimes, for some unknown reason, some browsers receive
            // the annotation value as an array-like object :-\
      var description = Array.prototype.join.call(rawDescription, '')

      for (var i = 0; i < annotations.length; i++) {
        if (annotations[i] === description) {
          annotations.removeAt(i)
        }
      }
      model.set('annotations', annotations)
      model.save().then(function (model) {
        self.get('applicationController').hideLoading()
        model.reload()
      }, function (reason) {
        model.rollbackAttributes()
        self.get('applicationController').hideLoading()
        self.get('applicationController').error_message(
                    'Could not delete annotation!'
                )
      })
    },
    'start': function () {
      var model = this.get('model')
      var url = this.store.adapterFor('task').buildURL('task', model.get('uuid')) + 'start/'

      return this.ajaxRequest({
        url: url,
        type: 'POST'
      }).then(function () {
        model.reload()
      }, function (msg) {
        model.reload()
        this.get('applicationController').error_message(
                    `An error was encountered while ` +
                    `attempting to start your task: ${msg}`
                )
      }.bind(this))
    },
    'stop': function () {
      var model = this.get('model')
      var url = this.store.adapterFor('task').buildURL('task', model.get('uuid')) + 'stop/'

      return this.ajaxRequest({
        url: url,
        type: 'POST'
      }).then(function () {
        model.reload()
      }, function (msg) {
        model.reload()
        this.get('applicationController').error_message(
                    `An error was encountered while ` +
                    `attempting to stop your task: ${msg}`
                )
      }.bind(this))
    },
    'delete': function () {
      var result = confirm('Are you sure you would like to delete this task?')
      if (result) {
        var model = this.get('model')
        var url = this.store.adapterFor('task').buildURL('task', this.get('uuid')) + 'delete/'
        this.get('applicationController').showLoading()

        return this.ajaxRequest({
          url: url,
          type: 'POST'
        }).then(function () {
          model.reload()
          this.get('tasksController').refresh()
          this.transitionToRoute('tasks')
        }.bind(this), function (msg) {
          model.reload()
          this.get('applicationController').error_message(
                        `An error was encountered while ` +
                        `attempting to delete your task: ${msg}`
                    )
        }.bind(this))
      }
    }
  }
})

export default controller
