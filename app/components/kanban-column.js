import Ember from "ember";

var component = Ember.Component.extend({
    componentName: 'Test',
    columnName: function() {
        return this.column[0];
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

        debugger;

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
});

export default component;
