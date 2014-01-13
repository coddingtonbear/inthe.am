var model = DS.Model.extend({
  logged_in: DS.attr('boolean'),
  uid: DS.attr('string'),
  email: DS.attr('string'),
  configured: DS.attr('boolean'),
});

module.exports = model;
