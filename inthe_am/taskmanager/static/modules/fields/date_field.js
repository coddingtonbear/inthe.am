var field = Ember.TextField.extend({
  moment_format: 'YYYY-MM-DD HH:mm',
  picker_format: 'Y-m-d H:i',
  init: function() {
    this._super();
    this.updateModel();
  },
  updateModel: function(){
    var raw_value = this.get('date');
    var value = moment(raw_value);
    if (!raw_value || !value.isValid()) {
      this.set('value', '');
    } else {
      this.set('value', value.format(this.moment_format));
    }
  }.observes('identity'),
  updateDate: function(){
    var raw_value = this.get('value');
    if (raw_value.length === 0) {
      this.set('date', '');
    } else {
      var value = moment(raw_value);
      if (value.isValid()) {
        this.set('date', value.toDate());
      }
    }
  }.observes('value'),
  didInsertElement: function(){
    if($(document).width() > 350) {
      this.$().datetimepicker({
        format: this.picker_format,
        allowBlank: true
      });
    }
  }
});

module.exports = field;
