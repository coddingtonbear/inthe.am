var controller = Ember.ArrayController.extend({
  needs: ['application', 'task'],
  sortProperties: ['urgency'],
  sortAscending: false,
  defaultFilter: {
    fields: {
      'status': 'pending'
    },
    description: [],
    tags: [],
  },
  refresh: function(){
    // Refresh each entry to see if it has been closed.
    this.get('content').forEach(function(model){
      try {
        model.reload()
      } catch(e) {
        // pass
      }
    });

    // Then, request a new list from the endpoint to make sure
    // we gather any new tasks, too.
    var content = this.get('content');
    try {
        content.update();
    } catch(e) {
        // This should happen only when we haven't yet loaded this view.
    }
  },
  collectionObserver: function() {
    // If the collection has changed, and we're currently on the tasks
    // view, transition to showing the first task.
    var path = this.get('controllers.application').getHandlerPath();
    if(path == 'application.tasks.tasks.index') {
        Ember.run.debounce(this, 'transitionToFirstTask', 100);
    }
  }.observes('model.length'),
  transitionToFirstTask: function() {
    var task = this.get('pendingTasks.firstObject');
    if(task) {
      this.transitionToRoute('task', task);
    }
  },
  enteredFilters: function() {
    var value = this.get('filterString');
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
        filters.fields[key] = value;
      } else {
        filters.description.push(value);
      }
    });
    return filters;
  }.property('filterString'),
  pendingTasks: function() {
    var filters = this.get('enteredFilters');
    var result = this.get('model').filter(function(item, idx, enumerable) {
      var ok = true;

      Object.getOwnPropertyNames(filters.fields).forEach(function(field) {
        var filter_value = filters.fields[field];
        var item_value = item.get(field);
        if(item_value instanceof Date) {
          item_value = moment(item_value).format('YYYY-MM-DDTHH:mm:ssZ')
          if(filter_value == 'today') {
            filter_value = moment().format('YYYY-MM-DD');
          } else if(filter_value == 'tomorrow') {
            filter_value = moment().add('days', 1).format('YYYY-MM-DD');
          }
        }

        try {
            if(!item_value || item_value.indexOf(filter_value) !== 0) {
                ok = false;
            }
        }catch(e) {
            // This means we tried to filter a non-string value :-|
            ok = false;
        }
      });
      if(!ok) {
        return ok;
      }

      filters.tags.forEach(function(tag) {
        if(item.get('tags').indexOf(tag) < 0) {
          ok = false;
        }
      });
      if(!ok) {
        return ok;
      }

      var description = filters.description.join(' ');
      if(description && item.get('description').indexOf(description) < 0) {
        ok = false;
      }

      return ok;
    });

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
  actions: {
    prev_task: function() {
      var current_id = this.get('controllers.task.model.id');
      var array = this.get('pendingTasks');
      var last_task = null;
      var target_task = null;
      array.forEach(function(item, idx, enumerable){
        if(item.get('id') == current_id) {
          target_task = last_task;
        }
        last_task = item;
      }.bind(this));
      if(target_task) {
        this.transitionToRoute('task', target_task);
      }
    },
    next_task: function() {
      var current_id = this.get('controllers.task.model.id');
      var array = this.get('pendingTasks');
      var found_my_id = false;
      var target_task = null;
      array.forEach(function(item, idx, enumerable){
        if(found_my_id && target_task == null) {
          target_task = item;
        }
        if(item.get('id') == current_id) {
          found_my_id = true;
        }
      }.bind(this));
      if(target_task) {
        this.transitionToRoute('task', target_task);
      }
    }
  }
});

module.exports = controller;
