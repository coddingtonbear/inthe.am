var model = DS.Model.extend({
  md5hash: DS.attr('string'),
  last_seen: DS.attr('date'),
  created: DS.attr('date'),
  error: DS.attr('boolean'),
  message: DS.attr('string'),
  count: DS.attr('number')
});

module.exports = model;
