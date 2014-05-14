var get = Ember.get, set = Ember.set;

DS.DjangoTastypieSerializer = DS.RESTSerializer.extend({

  keyForAttribute: function(attr) {
    return Ember.String.decamelize(attr);
  },

  keyForRelationship: function(attr) {
    return Ember.String.decamelize(attr);
  },

  /**
    Tastypie adapter does not support the sideloading feature
    */
  extract: function(store, type, payload, id, requestType) {
    this.extractMeta(store, type, payload);

    var specificExtract = "extract" + requestType.charAt(0).toUpperCase() + requestType.substr(1);
    return this[specificExtract](store, type, payload, id, requestType);
  },

  extractMany: function(loader, json, type, records) {
    this.sideload(loader, type, json);
    this.extractMeta(loader, type, json);

    if (json.objects) {
      var objects = json.objects, references = [];
      if (records) { records = records.toArray(); }

      for (var i = 0; i < objects.length; i++) {
        if (records) { loader.updateId(records[i], objects[i]); }
        var reference = this.extractRecordRepresentation(loader, type, objects[i]);
        references.push(reference);
      }

      loader.populateArray(references);
    }
  },

  // Tastypie defaults do not support sideloading
  sideload: function(loader, type, json, root) {
  },

  resourceUriToId: function (resourceUri) {
    return resourceUri.split('/').reverse()[1];
  },

  normalizeId: function (hash) {
    if (hash.resource_uri) {
      hash.id = this.resourceUriToId(hash.resource_uri);
      delete hash.resource_uri;
    }
  },

  normalizeRelationships: function (type, hash) {
    var payloadKey, key, self = this;

    type.eachRelationship(function (key, relationship) {
      if (this.keyForRelationship) {
        payloadKey = this.keyForRelationship(key, relationship.kind);
        if (key !== payloadKey) {
          hash[key] = hash[payloadKey];
          delete hash[payloadKey];
        }
      }
      if (hash[key]) {
        if (relationship.kind === 'belongsTo'){
          hash[key] = this.resourceUriToId(hash[key]);
        } else if (relationship.kind === 'hasMany'){
          var ids = [];
          hash[key].forEach(function (resourceUri){
            ids.push(self.resourceUriToId(resourceUri));
          });
          hash[key] = ids;
        }
      }
    }, this);
  },

  extractArray: function(store, primaryType, payload) {
    var records = [];
    var self = this;
    payload.objects.forEach(function (hash) {
      self.extractEmbeddedFromPayload(store, primaryType, hash);
      records.push(self.normalize(primaryType, hash, primaryType.typeKey));
    });
    return records;
  },

  extractSingle: function(store, primaryType, payload, recordId, requestType) {
    var newPayload = {};
    this.extractEmbeddedFromPayload(store, primaryType, payload);
    newPayload[primaryType.typeKey] = payload;

    return this._super(store, primaryType, newPayload, recordId, requestType);
  },

  isEmbedded: function(config) {
    return !!config && (config.embedded === 'load' || config.embedded === 'always');
  },

  extractEmbeddedFromPayload: function(store, type, payload) {
    var self = this;
    var attrs = get(this, 'attrs');

    if (!attrs) { return; }

    type.eachRelationship(function(key, relationship) {
      var config = attrs[key];

      if (self.isEmbedded(config)) {
        if (relationship.kind === 'hasMany') {
          self.extractEmbeddedFromHasMany(store, key, relationship, payload, config);
        } else if (relationship.kind === 'belongsTo') {
          self.extractEmbeddedFromBelongsTo(store, key, relationship, payload, config);
        }
      }
    });
  },

  extractEmbeddedFromHasMany: function(store, key, relationship, payload, config) {
    var self = this;
    var serializer = store.serializerFor(relationship.type.typeKey),
    primaryKey = get(this, 'primaryKey');

    key = config.key ? config.key : this.keyForAttribute(key);

    var ids = [];

    if (!payload[key]) {
      return;
    }

    Ember.EnumerableUtils.forEach(payload[key], function(data) {
      var embeddedType = store.modelFor(relationship.type.typeKey);

      serializer.extractEmbeddedFromPayload(store, embeddedType, data);

      data = serializer.normalize(embeddedType, data, embeddedType.typeKey);

      ids.push(serializer.relationshipToResourceUri(relationship, data));
      store.push(embeddedType, data);
    });

    payload[key] = ids;
  },

  extractEmbeddedFromBelongsTo: function(store, key, relationship, payload, config) {
    var serializer = store.serializerFor(relationship.type.typeKey),
      primaryKey = get(this, 'primaryKey');

    key = config.key ? config.key : this.keyForAttribute(key);

    if (!payload[key]) {
      return;
    }

    var data = payload[key];
    var embeddedType = store.modelFor(relationship.type.typeKey);

    serializer.extractEmbeddedFromPayload(store, embeddedType, data);

    data = serializer.normalize(embeddedType, data, embeddedType.typeKey);
    payload[key] = serializer.relationshipToResourceUri(relationship, data);

    store.push(embeddedType, data);
  },

  relationshipToResourceUri: function (relationship, value){
    if (!value)
      return value;

    var store = relationship.type.store,
        typeKey = relationship.type.typeKey;

    return store.adapterFor(typeKey).buildURL(typeKey, get(value, 'id'));
  },

  serializeIntoHash: function (data, type, record, options) {
    Ember.merge(data, this.serialize(record, options));
  },

  serializeBelongsTo: function (record, json, relationship) {
    this._super.apply(this, arguments);
    var key = relationship.key;
    key = this.keyForRelationship ? this.keyForRelationship(key, "belongsTo") : key;

    json[key] = this.relationshipToResourceUri(relationship, get(record, relationship.key));
  },

  serializeHasMany: function(record, json, relationship) {
    var key = relationship.key,
    attrs = get(this, 'attrs'),
    config = attrs && attrs[key] ? attrs[key] : false;
    key = this.keyForRelationship ? this.keyForRelationship(key, "belongsTo") : key;

    var relationshipType = DS.RelationshipChange.determineRelationshipType(record.constructor, relationship);

    if (relationshipType === 'manyToNone' || relationshipType === 'manyToMany' || relationshipType === 'manyToOne') {
      if (this.isEmbedded(config)) {
        json[key] = get(record, key).map(function (relation) {
          var data = relation.serialize();

          // Embedded objects need the ID for update operations
          var id = relation.get('id');
          if (!!id) { data.id = id; }

          return data;
        });
      } else {
        json[key] = get(record, relationship.key).map(function (next){
          return this.relationshipToResourceUri(relationship, next);
        }, this);
      }
    }
  }
});


var get = Ember.get, set = Ember.set;

function rejectionHandler(reason) {
  Ember.Logger.error(reason, reason.message);
  throw reason;
}

DS.DjangoTastypieAdapter = DS.RESTAdapter.extend({
  /**
    Set this parameter if you are planning to do cross-site
    requests to the destination domain. Remember trailing slash
  */
  serverDomain: null,

  /**
    This is the default Tastypie namespace found in the documentation.
    You may change it if necessary when creating the adapter
  */
  namespace: "api/v1",

  /**
    Bulk commits are not supported at this time by the adapter.
    Changing this setting will not work
  */
  bulkCommit: false,

  /**
    Tastypie returns the next URL when all the elements of a type
    cannot be fetched inside a single request. Unless you override this
    feature in Tastypie, you don't need to change this value. Pagination
    will work out of the box for findAll requests
  */
  since: 'next',

  /**
    Serializer object to manage JSON transformations
  */
  defaultSerializer: '_djangoTastypie',

  buildURL: function(record, suffix) {
    var url = this._super(record, suffix);

    // Add the trailing slash to avoid setting requirement in Django.settings
    if (url.charAt(url.length -1) !== '/') {
      url += '/';
    }

    // Add the server domain if any
    if (!!this.serverDomain) {
      url = this.removeTrailingSlash(this.serverDomain) + url;
    }

    return url;
  },

  findMany: function(store, type, ids) {
    return this.ajax('%@set/%@/'.fmt(this.buildURL(type.typeKey), ids.join(';')),
                     'GET');
  },


  /**
     The actual nextUrl is being stored. The offset must be extracted from
     the string to do a new call.
     When there are remaining objects to be returned, Tastypie returns a
     `next` URL that in the meta header. Whenever there are no
     more objects to be returned, the `next` paramater value will be null.
     Instead of calculating the next `offset` each time, we store the nextUrl
     from which the offset will be extrated for the next request
  */
  sinceQuery: function(since) {
    var offsetParam,
        query;

    query = {};

    if (!!since) {
      offsetParam = since.match(/offset=(\d+)/);
      offsetParam = (!!offsetParam && !!offsetParam[1]) ? offsetParam[1] : null;
      query.offset = offsetParam;
    }

    return offsetParam ? query : null;
  },

  removeTrailingSlash: function(url) {
    if (url.charAt(url.length -1) === '/') {
      return url.slice(0, -1);
    }
    return url;
  },

  /**
    django-tastypie does not pluralize names for lists
  */
  pathForType: function(type) {
    return type;
  }
});
