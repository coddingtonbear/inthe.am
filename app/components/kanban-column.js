import Ember from "ember";

var component = Ember.Component.extend({
    SORT_ORDER: 'intheamkanbansortorder',
    COLUMN: 'intheamkanbancolumn',
    componentName: 'Test',
    columnName: function() {
        return this.column[0];
    }.property('column'),
    columnStatus: function() {
        return this.column[1];
    }.property('column'),
    columnTasks: function() {
        var tasks = Ember.ArrayProxy.create(
            {
                content: [],
            }
        );
        var lowestId = 0;

        this.get('tasks').then(function(allTasks){
            var tasksNeedingSortOrders = [];
            allTasks = allTasks.sortBy(this.SORT_ORDER);
            allTasks.forEach(function(task) {
                if(this.taskMatchesColumn(task, this.get('columnName'))) {
                    var sortOrder = task.get(this.SORT_ORDER);
                    if(! sortOrder) {
                        tasksNeedingSortOrders.pushObject(task);
                    } else {
                        if (sortOrder === lowestId) {
                            task.set(this.SORT_ORDER, ++lowestId);
                        } else if (sortOrder > lowestId) {
                            lowestId = sortOrder;
                        }
                    }
                    tasks.pushObject(task);
                }
            }.bind(this));

            tasks.set('content', tasks.content.sort(function(a, b){
                if(a.get(this.SORT_ORDER) < b.get(this.SORT_ORDER)) {
                    return -1;
                } else if(b.get(this.SORT_ORDER) < a.get(this.SORT_ORDER)) {
                    return 1;
                } else {
                    return 0;
                }
            }.bind(this)));

            tasksNeedingSortOrders.forEach(function(task) {
                task.set(this.SORT_ORDER, ++lowestId);
                task.save();
            }.bind(this));
        }.bind(this));

        return tasks;
    }.property('model'),
    getKnownColumns: function() {
        var columns = [];
        this.allColumns.forEach(function(col) {
            columns.pushObject(col[0]);
        }.bind(this));
        return columns;
    },
    taskMatchesColumn: function(task, columnName) {
        var allColumns = this.getKnownColumns();
        var taskColumn = task.get(this.COLUMN);

        if (
            allColumns.indexOf(taskColumn) === -1 ||
            taskColumn === null
        ) {
            taskColumn = '';
        }
        if (columnName === 'Backlog') {
            columnName = '';
        }
        if (taskColumn === columnName) {
            return true;
        }
        return false;
    },
    getTaskForItem: function(item) {
        if(item) {
            return this.get('targetObject.store').find(
                'kanban-task', item.getAttribute('data-uuid')
            );
        } else {
            // Return a promise returning a null response if no
            // item was passed-in.
            return new Ember.RSVP.Promise(function(resolve, reject){
                resolve(null);
            });
        }
    },
    updateTaskSortOrder: function(evt) {
        var newIndex = evt.newIndex;
        var nodes = this.$().find('.kanban-task');
        return Ember.RSVP.Promise.all(
            [
                this.getTaskForItem(evt.item),
                this.getTaskForItem(
                    nodes[newIndex-1]
                ),
                this.getTaskForItem(
                    nodes[newIndex+1]
                ),
            ]
        ).then(function(values){
            var [thisElement, prevElement, nextElement] = values;
            var [prevValue, thisValue] = [0, 0];
            if(!prevElement) {
                prevValue = 0;
            } else {
                prevValue = prevElement.get(this.SORT_ORDER);
            }
            if(!nextElement) {
                thisValue = prevValue + 1;
            } else {
                thisValue = prevValue + (
                    (
                        nextElement.get(this.SORT_ORDER) - prevValue
                    ) / 2
                );
            }

            thisElement.set(this.SORT_ORDER, thisValue);
            return thisElement;
        }.bind(this));
    },
    taskMoved: function(evt) {
        this.updateTaskSortOrder(evt).then(function(thisElement){
            thisElement.save();
        });
    },
    taskRemoved: function(evt) {
        /* This is a no-op for now.  All task transformations
         * will take place when the task is added to the destination
         * list.
         */
    },
    taskAdded: function(evt) {
        var destinationStatus = this.get('columnStatus');
        this.updateTaskSortOrder(evt).then(function(item) {
            item.set(this.COLUMN, this.get('columnName'));
            if(destinationStatus) {
                item.set('status', destinationStatus);
            }
            item.save();
        }.bind(this));
    },
    didInsertElement: function() {
        this.set(
            'sortable',
            Sortable.create(
                this.$().find('.kanban-tasks')[0],
                {
                    animation: 150,
                    onUpdate: this.taskMoved.bind(this),
                    onRemove: this.taskRemoved.bind(this),
                    onAdd: this.taskAdded.bind(this),
                    group: 'kanbanColumn',
                }
            )
        );
    },
});

export default component;
