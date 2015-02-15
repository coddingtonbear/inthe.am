import Ember from "ember";

var component = Ember.Component.extend({
    componentName: 'Test',
    columnName: function() {
        return this.column[0];
    }.property('column'),
    columnStatus: function() {
        return this.column[1];
    }.property('column'),
    columnTasks: function() {
        var tasks = [];
        this.get('tasks').then(function(allTasks){
            allTasks.forEach(function(task) {
                if(this.taskMatchesColumn(task, this.get('columnName'))) {
                    tasks.pushObject(task);
                }
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
        var taskColumn = task.get('intheamkanbancolumn');

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
        return this.get('targetObject.store').find(
            'kanban-task', item.getAttribute('data-uuid')
        );
    },
    taskMoved: function(evt) {
        console.log("TaskMoved is not implemented", evt);
    },
    taskRemoved: function(evt) {
        /* This is a no-op for now.  All task transformations
         * will take place when the task is added to the destination
         * list.
         */
    },
    taskAdded: function(evt) {
        var destinationStatus = this.get('columnStatus');
        this.getTaskForItem(evt.item).then(function(item) {
            item.set('intheamkanbancolumn', this.get('columnName'));
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
