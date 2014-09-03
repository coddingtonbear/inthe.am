var controller = Ember.ArrayController.extend({
  sortProperties: ['urgency'],
  sortAscending: false,
  defaultFilter: {
    fields: [
      ['status', 'pending']
    ],
    description: [],
    tags: [],
  },
  refresh: function(){
    try {
      this.get('content').update();
    } catch(e) {
      // Pass
    }
  },
  getFilters: function(value) {
    var filters = JSON.parse(
      JSON.stringify(this.defaultFilter)
    );

    if(!value) {
      return filters;
    }

    var raw_tokens = value.split(' ');
    $.each(raw_tokens, function(idx, value) {
      var colon = value.indexOf(':');
      if(value.substring(0, 1) == '+') {
        filters.tags.push(value.substring(1));
      } else if (colon > -1) {
        var this_filter = {};
        key = value.substring(0, colon);
        value = value.substring(colon + 1);
        filters.fields.push([key, value]);
      } else {
        filters.description.push(value);
      }
    });
    return filters;
  },
  pendingTasks: function() {
    console.log('Test');
    var filters = this.getFilters(this.get('filterString'));
    var result = this.get('model').filter(function(item, idx, enumerable) {
      var ok = true;

      filters.fields.forEach(function(field_set) {
        var field = field_set[0];
        var value = field_set[1];

        if(item.get(field).indexOf(value) !== 0) {
            ok = false;
        }
      });

      filters.tags.forEach(function(tag) {
        if(item.get('tags').indexOf(tag) < 0) {
          ok = false;
        }
      });

      var description = filters.description.join('');
      if(description && item.get('description').indexOf(description) < 0) {
        ok = false;
      }

      return ok;
    });

    console.log(result);

    var sortedResult = Em.ArrayProxy.createWithMixins(
      Ember.SortableMixin,
      {
        content:result,
        sortProperties: this.sortProperties,
        sortAscending: false
      }
    );
    return sortedResult;
  }.property('model.@each.status'),
  init: function() {
    Ember.run.next(this, function(){
      var self = this;
      $('#filter-string').keyup(function() {
        console.log('Changed', self, this);
        self.set('filterString', this.value);
        self.notifyPropertyChange('pendingTasks');
      });
    });
  }
});

module.exports = controller;
