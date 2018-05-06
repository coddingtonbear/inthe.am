import Ember from 'ember'

export default Ember.Helper.helper(function ([uda]) {
  if (uda.type === 'DateField') {
    if (uda.value) {
      return new Ember.Handlebars.SafeString(
                '<span class="calendar date" title="' + moment(uda.value).format('LLLL') + '">' + moment(uda.value).calendar() + '</span>'
            )
    }
  } else if (uda.type === 'StringField') {
    return new Ember.Handlebars.SafeString(linkify(uda.value))
  }
  return uda.value
})
