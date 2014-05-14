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
    } else if (moment().format('L') === moment(this.get('due')).format('L')) {
      value = 'due__today';
    } else if ( // Truncate date to date only
        moment(
          moment().format('YYYYMMDD'),
          'YYYYMMDD'
        ).add('days', 7).isAfter(this.get('due'))
    ) {
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
        if ($.inArray(item.get('status'), ['completed', 'deleted']) > -1) {
          return false;
        }
        return true;
      }
    );
  }.property('dependent_tickets'),

  is_blocking: function() {
    return this.get('blocked_tickets').any(
      function(item, idx, enumerable) {
        if ($.inArray(item.get('status'), ['completed', 'deleted']) > -1) {
          return false;
        }
        return true;
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

  ticketIdsToObjects: function(value) {
    var promises = [];
    if (value) {
      var ticket_ids = value.split(',');
      for (var i = 0; i < ticket_ids.length; i++) {
        promises.pushObject(
          this.store.find('task', ticket_ids[i])
        );
      }
    }
    return Ember.RSVP.Promise.all(promises);
  },

  dependent_tickets: function(){
    return DS.PromiseArray.create({
      promise: this.ticketIdsToObjects(
        this.get('depends')
      )
    });
  }.property('depends'),

  blocked_tickets: function(){
    return DS.PromiseArray.create({
      promise: this.ticketIdsToObjects(
        this.get('blocks')
      )
    });
  }.property('blocks'),

  as_json: function() {
    return JSON.stringify(this.store.serialize(this));
  }.property()
});

module.exports = model;
