var model = DS.Model.extend({
  annotations: DS.attr(),
  description: DS.attr('string'),
  due: DS.attr('date'),
  entry: DS.attr('date'),
  modified: DS.attr('date'),
  priority: DS.attr('string'),
  resource_uri: DS.attr('string'),
  start: DS.attr('date'),
  'status': DS.attr('string'),
  urgency: DS.attr('number'),
  uuid: DS.attr('string'),
  depends: DS.attr('string'),

  editable: function(){
    if (this.get('status') == 'pending') {
      return true;
    }
    return false;
  }.property('status'),

  icon: function(){
    if (this.get('status') == 'completed') {
      return 'fa-check-square-o';
    } else {
      return 'fa-square-o';
    }
  }.property('status', 'urgency'),

  processed_annotations: function() {
    var value = this.get('annotations');
    if (value) {
      for (var i = 0; i < value.length; i++) {
        value[i] = {
          entry: new Date(Ember.Date.parse(value[i].entry)),
          description: value[i].description
        };
      }
    } else {
      return [];
    }
    return value;
  }.property('annotations'),

  dependent_tickets: function(){
    var value = this.get('depends');
    var values = [];
    if (value) {
      var ticket_ids = value.split(',');
      for(var i = 0; i < ticket_ids.length; i++) {
        values[values.length] = this.store.find('task', ticket_ids[i]);
      }
      return values;
    } else {
      return [];
    }
  }.property('depends')
});

module.exports = model;
