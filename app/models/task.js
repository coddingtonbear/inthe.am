import DS from "ember-data";

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
    short_id: DS.attr('number'),
    depends: DS.attr(),
    blocks: DS.attr(),
    project: DS.attr('string'),
    imask: DS.attr('number'),
    udas: DS.attr(),

    editable: function(){
        if (this.get('status') === 'pending') {
            return true;
        } else if (this.get('status') === 'waiting') {
            return true;
        }
        return false;
    }.property('status'),

    icon: function() {
        if (this.get('status') === 'completed') {
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
        this.get('calculateIsBlocked').bind(this)();
        this.get('calculateIsBlocking').bind(this)();
        var value = '';
        if (this.get('start')) {
            value = 'active';
        } else if (this.get('is_blocking') === true) {
            value = 'blocking';
        } else if (this.get('is_blocked') === true) {
            value = 'blocked';
        } else if (moment(this.get('due')).isBefore(moment())) {
            value = 'overdue';
        } else if (moment().format('L') === moment(this.get('due')).format('L')) {
            value = 'due__today';
        } else if ( // Truncate date to date only
                moment(
                    moment().format('YYYYMMDD'),
                    'YYYYMMDD'
                ).add(7, 'days').isAfter(this.get('due'))
        ) {
            value = 'due';
        } else if (this.get('imask')) {
            value = 'recurring';
        } else if (this.get('priority') === 'H') {
            value = 'pri__H';
        } else if (this.get('priority') === 'M') {
            value = 'pri__M';
        } else if (this.get('priority') === 'L') {
            value = 'pri__L';
        } else if (this.get('tags') && this.get('tags').length > 0) {
            value = 'tagged';
        }
        return value;
    }.property('status', 'urgency', 'start', 'due', 'is_blocked', 'is_blocking'),

    calculateIsBlocked: function() {
        var self = this;
        this.get('dependent_tickets').then(function(tix){
            var result = tix.any(function(item, idx, enumerable) {
                if ($.inArray(item.get('status'), ['completed', 'deleted']) > -1) {
                    return false;
                }
                return true;
            });
            self.set('is_blocked', result);
        });
    },

    calculateIsBlocking: function() {
        var self = this;
        this.get('blocked_tickets').then(function(tix){
            var result = tix.any(function(item, idx, enumerable) {
                if ($.inArray(item.get('status'), ['completed', 'deleted']) > -1) {
                    return false;
                }
                return true;
            });
            self.set('is_blocking', result);
        });
    },

    ticketIdsToObjects: function(value) {
        var promises = [];
        if (value) {
            for (var i = 0; i < value.length; i++) {
                promises.pushObject(
                    this.store.findRecord('task', value[i])
                );
            }
        }
        return DS.PromiseArray.create({
            promise: Ember.RSVP.Promise.all(promises, 'TicketIDs ' + value + ' to Objects')
        });
    },

    dependent_tickets: function(){
        return this.ticketIdsToObjects(this.get('depends'));
    }.property('depends'),

    blocked_tickets: function(){
        return this.ticketIdsToObjects(this.get('blocks'));
    }.property('blocks'),

    as_json: function() {
        return JSON.stringify(this.store.serialize(this));
    }.property()
});

export default model;
