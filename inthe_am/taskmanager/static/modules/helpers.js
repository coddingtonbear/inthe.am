
Ember.Handlebars.registerHelper('comma_to_list', function(item, options){
  return item.split(',');
});

Ember.Handlebars.registerHelper('propercase', function(string, options) {
  var project_name = options.contexts[0].get(string);
  var properCase = function(txt) {
    return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
  };
  return project_name.replace('_', ' ').replace(/\w\S*/g, properCase);
});

Ember.Handlebars.registerHelper('calendar', function(string, options) {
  var date;
  try{
    date = options.contexts[0].get(string);
  }catch(e) {
    date = options.contexts[0][string];
  }
  if (date) {
    return new Handlebars.SafeString('<span class="calendar date" title="' + moment(date).format('LLLL') + '">' + moment(date).calendar() + "</span>");
  }
});
