import Ember from "ember";
import ArrayController from "ember-legacy-controllers/array";

var controller = ArrayController.extend({
  taskController: Ember.inject.controller("task"),
  applicationController: Ember.inject.controller("application"),
  sortProperties: ["urgency:desc"],
  sortAscending: false,
  defaultFilter: {
    fields: {
      status: "pending",
    },
    description: [],
    tags: [],
  },
  ajaxRequest: function (params) {
    return this.get("applicationController").ajaxRequest(params);
  },
  refresh: function () {
    // First, request a synchronous sync
    return this.ajaxRequest({
      url: this.get("applicationController").urls.sync,
      type: "POST",
    }).then(
      function () {
        // Then, request a new list from the endpoint to make sure
        // we gather any new tasks, too.
        this.store.findAll("task").then(
          function () {
            // Refresh each entry to see if it has been closed.
            this.get("content").forEach(function (model) {
              try {
                model.reload();
              } catch (e) {
                // pass
              }
            });
          }.bind(this)
        );
      }.bind(this),
      function (msg) {
        this.get("applicationController").error_message(
          `An error was encountered while ` +
            `attempting to synchronize your task list: ${msg}`
        );
      }.bind(this)
    );
  },
  collectionObserver: function () {
    // If the collection has changed, and we're currently on the tasks
    // view, transition to showing the first task.
    var path = this.get("applicationController").getHandlerPath();
    if (path === "application.tasks.tasks.index") {
      Ember.run.debounce(this, "transitionToFirstTask", 100);
    }
  }.observes("model.length"),
  transitionToFirstTask: function () {
    var task = this.get("pendingTasks.firstObject");
    if (task) {
      this.transitionToRoute("task", task);
    }
  },
  enteredFilters: Ember.computed("filterString", function () {
    var value = this.get("filterString");
    var filters = JSON.parse(JSON.stringify(this.get("defaultFilter")));

    if (!value) {
      return filters;
    }

    var raw_tokens = value.split(" ");
    $.each(raw_tokens, function (idx, value) {
      var colon = value.indexOf(":");
      if (value.slice(0, 1) === "+") {
        filters.tags.push(value.slice(1));
      } else if (colon > -1) {
        var key = value.slice(0, colon);
        var sliced_value = value.slice(colon + 1);
        filters.fields[key] = sliced_value;
      } else {
        filters.description.push(value);
      }
    });
    return filters;
  }),
  unsortedPendingTasks: Ember.computed(
    "enteredFilters",
    "model.@each.status",
    function () {
      var filters = this.get("enteredFilters");
      var result = this.get("model").filter(function (item, idx, enumerable) {
        var ok = true;

        Object.getOwnPropertyNames(filters.fields).forEach(function (field) {
          var filter_value = filters.fields[field];
          var item_value = item.get(field);
          if (item_value instanceof Date) {
            item_value = moment.utc(item_value).format("YYYY-MM-DDTHH:mm:ssZ");
            if (filter_value === "today") {
              filter_value = moment().format("YYYY-MM-DD");
            } else if (filter_value === "tomorrow") {
              filter_value = moment().add(1, "days").format("YYYY-MM-DD");
            }
          }

          try {
            if (!item_value || item_value.indexOf(filter_value) !== 0) {
              ok = false;
            }
          } catch (e) {
            // This means we tried to filter a non-string value :-|
            ok = false;
          }
        });
        if (!ok) {
          return ok;
        }

        filters.tags.forEach(function (tag) {
          if (!item.get("tags") || item.get("tags").indexOf(tag) < 0) {
            ok = false;
          }
        });
        if (!ok) {
          return ok;
        }

        var description = filters.description.join(" ");
        if (description && item.get("description").indexOf(description) < 0) {
          ok = false;
        }

        return ok;
      });

      return result;
    }
  ),
  pendingTasks: Ember.computed.sort("unsortedPendingTasks", "sortProperties"),
  actions: {
    prev_task: function () {
      var current_id = this.get("taskController.model.id");
      var array = this.get("pendingTasks");
      var last_task = null;
      var target_task = null;
      array.forEach(function (item, idx, enumerable) {
        if (item.get("id") === current_id) {
          target_task = last_task;
        }
        last_task = item;
      });
      if (target_task) {
        this.transitionToRoute("task", target_task);
      }
    },
    next_task: function () {
      var current_id = this.get("taskController.model.id");
      var array = this.get("pendingTasks");
      var found_my_id = false;
      var target_task = null;
      array.forEach(function (item, idx, enumerable) {
        if (found_my_id && target_task == null) {
          target_task = item;
        }
        if (item.get("id") === current_id) {
          found_my_id = true;
        }
      });
      if (target_task) {
        this.transitionToRoute("task", target_task);
      }
    },
  },
});

export default controller;
