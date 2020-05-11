import DS from 'ember-data'

var model = DS.Model.extend({
  logged_in: DS.attr('boolean'),
  uid: DS.attr('string'),
  username: DS.attr('string'),
  name: DS.attr('string'),
  email: DS.attr('string'),
  configured: DS.attr('boolean'),
  taskd_credentials: DS.attr('string'),
  taskd_server: DS.attr('string'),
  api_key: DS.attr('string')
})

export default model
