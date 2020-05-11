import Ember from 'ember'

var controller = Ember.Controller.extend({
  applicationController: Ember.inject.controller('application'),
  ajaxRequest: function (params, returnAll) {
    return this.get('applicationController').ajaxRequest(params, returnAll)
  },
  actions: {
    get_file_from_url: function (url, filename) {
      return this.ajaxRequest({
        url: url,
        type: 'GET',
        data: {}
      }, true).then(function (data) {
        var xhr = data[2]
        var data = data[0]
        var element = document.createElement('a')
        element.setAttribute(
                    'href',
                    'data:' +
                    xhr.getResponseHeader('Content-Type') +
                    'charset=utf-8,' +
                    encodeURIComponent(data)
                )
        element.setAttribute(
                    'download',
                    filename
                )
        element.style.display = 'none'
        document.body.appendChild(element)
        element.click()

        document.body.removeChild(element)
      }, function (msg) {
        this.error_message(
                    `An error was encountered while ` +
                    `downloading your certificate: ${msg}`
                )
      }.bind(this))
    }
  }
})

export default controller
