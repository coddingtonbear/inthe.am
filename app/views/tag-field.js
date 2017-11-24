import Ember from 'ember'

var field = Ember.TextField.extend({
  init: function () {
    this._super()
    this.updateModel()
  },
  updateModel: function () {
    var value = this.get('tags')
    if (!value) {
      this.set('value', '')
    } else {
      this.set('value', value.join(' '))
    }
  }.observes('identity'),
  updateDate: function () {
    var value = this.get('value')
    if (value.length === 0) {
      this.set('tags', [])
    } else {
      var newArray = []
      var rawValues = value.split(' ')
      for (var i = 0; i < rawValues.length; i++) {
        if (rawValues[i] !== undefined && rawValues[i] !== null && rawValues[i] !== '') {
          newArray.push(rawValues[i])
        }
      }
      this.set('tags', newArray)
    }
  }.observes('value')
})

export default field
