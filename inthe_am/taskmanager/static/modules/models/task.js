var model = DS.Model.extend({
  annotations: DS.attr(),
  tags: DS.attr(),
  description: DS.attr('string'),
  due: DS.attr('date'),
  entry: DS.attr('date'),
  modified: DS.attr('date'),
  priority: DS.attr('string'),
  resource_uri: DS.attr('string'),
  start: DS.attr('date'),
  wait: DS.attr('date'),
  scheduled: DS.attr('date'),
  'status': DS.attr('string'),
  urgency: DS.attr('number'),
  uuid: DS.attr('string'),
  depends: DS.attr('string'),
  blocks: DS.attr('string'),
  project: DS.attr('string'),
  imask: DS.attr('number'),
  udas: DS.attr(),

  editable: function(){
    if (this.get('status') == 'pending') {
      return true;
    }
    return false;
  }.property('status'),

  icon: function() {
    if (this.get('status') == 'completed') {
      return 'fa-check-circle-o';
    } else if (this.get('start')) {
      return 'fa-asterisk';
    } else if (this.get('due')) {
      return 'fa-clock-o';
    } else {
      return 'fa-circle-o';
    }
  }.property('status', 'start', 'due'),

  taskwarrior_class: function() {
    var value = '';
    if (this.get('start')) {
      value = 'active';
    } else if (this.get('is_blocked')) {
      value = 'blocked';
    } else if (this.get('is_blocking')) {
      value = 'blocking';
    } else if (moment(this.get('due')).isBefore(moment())) {
      value = 'overdue';
    } else if (moment().add('hours', 24).isAfter(this.get('due'))) {
      value = 'due__today';
    } else if (moment().add('days', 7).isAfter(this.get('due'))) {
      value = 'due';
    } else if (this.get('imask')) {
      value = 'recurring';
    } else if (this.get('priority') == 'H') {
      value = 'pri__H';
    } else if (this.get('priority') == 'M') {
      value = 'pri__M';
    } else if (this.get('priority') == 'L') {
      value = 'pri__L';
    } else if (this.get('tags')) {
      value = 'tagged';
    }
    return value;
  }.property('status', 'urgency', 'start', 'due', 'is_blocked', 'is_blocking'),

  is_blocked: function() {
    return this.get('dependent_tickets').any(
      function(item, idx, enumerable) {
        if (item.get('status') == 'pending') {
          return true;
        }
        return false;
      }
    );
  }.property('dependent_tickets'),

  is_blocking: function() {
    return this.get('blocked_tickets').any(
      function(item, idx, enumerable) {
        if (item.get('status') == 'pending') {
          return true;
        }
        return false;
      }
    );
  }.property('blocked_tickets'),

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

  processed_udas: function() {
    var value = [];
    for(var v in this.get('udas')) {
      value.push(this.get('udas')[v]);
    }
    return value;
  }.property('udas'),

  _string_field_to_data: function(field_name, for_property) {
    var cached_value = this.get('_' + field_name);
    var value = this.get(field_name);
    var values = [];
    if (cached_value !== undefined) {
      return cached_value;
    } else {
      this.set('_' + field_name, values);
    }
    if (value) {
      var ticket_ids = value.split(',');
      var add_value_to_values = function(value) {
        var _for_property = for_property;
        values.pushObject(value);
        this.propertyDidChange(_for_property);
      };
      for (var i = 0; i < ticket_ids.length; i++) {
        this.store.find('task', ticket_ids[i]).then(
          add_value_to_values.bind(this)
        );
      }
      return values;
    } else {
      return [];
    }
  },

  dependent_tickets: function(){
    return this._string_field_to_data('depends', 'dependent_tickets');
  }.property('depends'),

  blocked_tickets: function(){
    return this._string_field_to_data('blocks', 'blocked_tickets');
  }.property('blocks'),

  as_json: function() {
    return JSON.stringify(this.store.serialize(this));
  }.property()
});

module.exports = model;
