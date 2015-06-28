import DS from "ember-data";

export default DS.DjangoTastypieAdapter.extend({
    namespace: 'api/v1',
});
