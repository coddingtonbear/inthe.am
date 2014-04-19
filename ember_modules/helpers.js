var App = require('./app');

Ember.Handlebars.helper('comma_to_list', function(item, options){
  return item.split(',');
});

Ember.Handlebars.helper('propercase', function(project_name, options) {
  if (project_name) {
    var properCase = function(txt) {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    };
    return project_name.replace('_', ' ').replace(/\w\S*/g, properCase);
  }
});

Ember.Handlebars.helper('calendar', function(date, options) {
  if (date) {
    return new Handlebars.SafeString('<span class="calendar date" title="' + moment(date).format('LLLL') + '">' + moment(date).calendar() + "</span>");
  }
});

Ember.Handlebars.helper('fromnow', function(date, options) {
  if (date) {
    return new Handlebars.SafeString('<span class="calendar date" title="' + moment(date).format('LLLL') + '">' + moment(date).fromNow() + "</span>");
  }
});

Ember.Handlebars.helper('markdown', function(html) {
  return new Handlebars.SafeString(markdown.toHTML(html));
});
