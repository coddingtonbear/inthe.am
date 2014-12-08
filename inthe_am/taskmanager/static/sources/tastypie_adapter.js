(function(global){
var define, requireModule, require, requirejs;

(function() {

  var _isArray;
  if (!Array.isArray) {
    _isArray = function (x) {
      return Object.prototype.toString.call(x) === "[object Array]";
    };
  } else {
    _isArray = Array.isArray;
  }
  
  var registry = {}, seen = {}, state = {};
  var FAILED = false;

  define = function(name, deps, callback) {
  
    if (!_isArray(deps)) {
      callback = deps;
      deps     =  [];
    }
  
    registry[name] = {
      deps: deps,
      callback: callback
    };
  };

  function reify(deps, name, seen) {
    var length = deps.length;
    var reified = new Array(length);
    var dep;
    var exports;

    for (var i = 0, l = length; i < l; i++) {
      dep = deps[i];
      if (dep === 'exports') {
        exports = reified[i] = seen;
      } else {
        reified[i] = require(resolve(dep, name));
      }
    }

    return {
      deps: reified,
      exports: exports
    };
  }

  requirejs = require = requireModule = function(name) {
    if (state[name] !== FAILED &&
        seen.hasOwnProperty(name)) {
      return seen[name];
    }

    if (!registry[name]) {
      throw new Error('Could not find module ' + name);
    }

    var mod = registry[name];
    var reified;
    var module;
    var loaded = false;

    seen[name] = { }; // placeholder for run-time cycles

    try {
      reified = reify(mod.deps, name, seen[name]);
      module = mod.callback.apply(this, reified.deps);
      loaded = true;
    } finally {
      if (!loaded) {
        state[name] = FAILED;
      }
    }

    return reified.exports ? seen[name] : (seen[name] = module);
  };

  function resolve(child, name) {
    if (child.charAt(0) !== '.') { return child; }

    var parts = child.split('/');
    var nameParts = name.split('/');
    var parentBase;

    if (nameParts.length === 1) {
      parentBase = nameParts;
    } else {
      parentBase = nameParts.slice(0, -1);
    }

    for (var i = 0, l = parts.length; i < l; i++) {
      var part = parts[i];

      if (part === '..') { parentBase.pop(); }
      else if (part === '.') { continue; }
      else { parentBase.push(part); }
    }

    return parentBase.join('/');
  }

  requirejs.entries = requirejs._eak_seen = registry;
  requirejs.clear = function(){
    requirejs.entries = requirejs._eak_seen = registry = {};
    seen = state = {};
  };
})();

define("ember-data-tastypie-adapter",
  ["ember-data-tastypie-adapter/tastypie_adapter","ember-data-tastypie-adapter/tastypie_serializer","exports"],
  function(__dependency1__, __dependency2__, __exports__) {
    "use strict";
    var DjangoTastypieAdapter = __dependency1__["default"];
    var DjangoTastypieSerializer = __dependency2__["default"];

    __exports__.DjangoTastypieAdapter = DjangoTastypieAdapter;
    __exports__.DjangoTastypieSerializer = DjangoTastypieSerializer;
  });
define("ember-data-tastypie-adapter/tastypie_adapter",
  ["exports"],
  function(__exports__) {
    "use strict";
    var get = Ember.get, set = Ember.set;
    var forEach = Ember.ArrayPolyfills.forEach;

    function rejectionHandler(reason) {
      Ember.Logger.error(reason, reason.message);
      throw reason;
    }

    var DjangoTastypieAdapter = DS.RESTAdapter.extend({
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
      defaultSerializer: '-django-tastypie',

      buildURL: function(type, id, record) {
        var url = this._super(type, id, record);

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

      findMany: function(store, type, ids, records) {
        return this.ajax(Ember.String.fmt('%@set/%@/', this.buildURL(type.typeKey), ids.join(';')),
                         'GET');
      },

      _stripIDFromURL: function(store, record) {
          var type = store.modelFor(record);
          var url = this.buildURL(type.typeKey, record.get('id'), record);

          var expandedURL = url.split('/');
          //Case when the url is of the format ...something/:id
          var lastSegment = expandedURL[ expandedURL.length - 2 ];
          var id = record.get('id');
          if (lastSegment === id) {
            expandedURL[expandedURL.length - 2] = "";
          } else if(endsWith(lastSegment, '?id=' + id)) {
            //Case when the url is of the format ...something?id=:id
            expandedURL[expandedURL.length - 1] = lastSegment.substring(0, lastSegment.length - id.length - 1);
          }

          return expandedURL.join('/');
        },

        /**
          http://stackoverflow.com/questions/417142/what-is-the-maximum-length-of-a-url-in-different-browsers
        */
        maxUrlLength: 2048,

        /**
          Organize records into groups, each of which is to be passed to separate
          calls to `findMany`.
          This implementation groups together records that have the same base URL but
          differing ids. For example `/comments/1` and `/comments/2` will be grouped together
          because we know findMany can coalesce them together as `/comments?ids[]=1&ids[]=2`
          It also supports urls where ids are passed as a query param, such as `/comments?id=1`
          but not those where there is more than 1 query param such as `/comments?id=2&name=David`
          Currently only the query param of `id` is supported. If you need to support others, please
          override this or the `_stripIDFromURL` method.
          It does not group records that have differing base urls, such as for example: `/posts/1/comments/2`
          and `/posts/2/comments/3`
          @method groupRecordsForFindMany
          @param {DS.Store} store
          @param {Array} records
          @return {Array}  an array of arrays of records, each of which is to be
                            loaded separately by `findMany`.
        */
        groupRecordsForFindMany: function (store, records) {
          var groups = Ember.MapWithDefault.create({defaultValue: function(){return [];}});
          var adapter = this;
          var maxUrlLength = this.maxUrlLength;

          forEach.call(records, function(record){
            var baseUrl = adapter._stripIDFromURL(store, record);
            groups.get(baseUrl).push(record);
          });

          function splitGroupToFitInUrl(group, maxUrlLength, paramNameLength) {
            var baseUrl = adapter._stripIDFromURL(store, group[0]);
            var idsSize = 0;
            var splitGroups = [[]];

            forEach.call(group, function(record) {
              var additionalLength = encodeURIComponent(record.get('id')).length + paramNameLength;
              if (baseUrl.length + idsSize + additionalLength >= maxUrlLength) {
                idsSize = 0;
                splitGroups.push([]);
              }

              idsSize += additionalLength;

              var lastGroupIndex = splitGroups.length - 1;
              splitGroups[lastGroupIndex].push(record);
            });

            return splitGroups;
          }

          var groupsArray = [];
          groups.forEach(function(group, key){
            var paramNameLength = '&ids%5B%5D='.length;
            var splitGroups = splitGroupToFitInUrl(group, maxUrlLength, paramNameLength);

            forEach.call(splitGroups, function(splitGroup) {
              groupsArray.push(splitGroup);
            });
          });

          return groupsArray;
        },

      /**
        sinceToken is defined by since property, which by default points to 'next' field in meta.
        We process this token to get the correct offset for loading more data.
        
      */
      findAll: function(store, type, sinceToken) {
        var query;

        if (sinceToken) {
          var offsetParam = sinceToken.match(/offset=(\d+)/);
          offsetParam = (!!offsetParam && !!offsetParam[1]) ? offsetParam[1] : null;
          query = { offset: offsetParam };
        }

        return this.ajax(this.buildURL(type.typeKey), 'GET', { data: query });
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

    __exports__["default"] = DjangoTastypieAdapter;
  });
define("ember-data-tastypie-adapter/tastypie_serializer",
  ["exports"],
  function(__exports__) {
    "use strict";
    var get = Ember.get, set = Ember.set;

    var DjangoTastypieSerializer = DS.RESTSerializer.extend({

      keyForAttribute: function(attr) {
        return Ember.String.decamelize(attr);
      },

      keyForRelationship: function(key, type) {
        return Ember.String.decamelize(key);
      },

      /**
        Tastypie adapter does not support the sideloading feature
        */
      extract: function(store, type, payload, id, requestType) {
        this.extractMeta(store, type, payload);

        var specificExtract = "extract" + requestType.charAt(0).toUpperCase() + requestType.substr(1);
        return this[specificExtract](store, type, payload, id, requestType);
      },
      
      /**
        `extractMeta` is used to deserialize any meta information in the
        adapter payload. By default Ember Data expects meta information to
        be located on the `meta` property of the payload object.
      
        The actual nextUrl is being stored. The offset must be extracted from
        the string to do a new call.
        When there are remaining objects to be returned, Tastypie returns a
        `next` URL that in the meta header. Whenever there are no
        more objects to be returned, the `next` paramater value will be null.
        Instead of calculating the next `offset` each time, we store the nextUrl
        from which the offset will be extrated for the next request
        
        @method extractMeta
        @param {DS.Store} store
        @param {subclass of DS.Model} type
        @param {Object} payload
      */
      extractMeta: function(store, type, payload) {
        if (payload && payload.meta) {
          var adapter = store.adapterFor(type);
                  
          if (adapter && adapter.get('since') !== null && payload.meta[adapter.get('since')] !== undefined) {
            payload.meta.since = payload.meta[adapter.get('since')];
          }
          
          store.metaForType(type, payload.meta);
          delete payload.meta;
        }
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
            var isEmbedded = self.isEmbedded(relationship);
            if (relationship.kind === 'belongsTo'){
              var resourceUri = hash[key];
              if (!isEmbedded) {
                              }
              hash[key] = self.resourceUriToId(hash[key]);
            } else if (relationship.kind === 'hasMany'){
              var ids = [];
              hash[key].forEach(function (resourceUri){
                if (!isEmbedded) {
                                  }
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

      isEmbedded: function(relationship) {
        var key = relationship.key;
        var attrs = get(this, 'attrs');
        var config = attrs && attrs[key] ? attrs[key] : false;
        if (config) {
            // Per model serializer will take preference for the embedded mode
            return (config.embedded === 'load' || config.embedded === 'always');
        }

        // Consider the resource as embedded if the relationship is not async
        return !(relationship.options.async ? relationship.options.async : false);
      },
      
      isResourceUri: function(adapter, payload) {
        if (typeof payload !== 'string') {
          return false;
        }
        return true;
      },

      extractEmbeddedFromPayload: function(store, type, payload) {
        var self = this;

        type.eachRelationship(function(key, relationship) {
          var attrs = get(self, 'attrs');
          var config = attrs && attrs[key] ? attrs[key] : false;

          if (self.isEmbedded(relationship)) {
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
        
        // Don't try to process data if it's not data!
        if (serializer.isResourceUri(store.adapterFor(relationship.type.typeKey), data)) {
          return;
        }
        
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
        var key = relationship.key;
        key = this.keyForRelationship ? this.keyForRelationship(key, "hasMany") : key;

        var relationshipType = record.constructor.determineRelationshipType(relationship);

        if (relationshipType === 'manyToNone' || relationshipType === 'manyToMany' || relationshipType === 'manyToOne') {
          if (this.isEmbedded(relationship)) {
            json[key] = get(record, key).map(function (relation) {
              var data = relation.serialize();

              // Embedded objects need the ID for update operations
              var id = relation.get('id');
              if (!!id) { data.id = id; }

              return data;
            });
          } else {
            var relationData = get(record, relationship.key); 
            
            // We can't deal with promises here. We need actual data
            if (relationData instanceof DS.PromiseArray) {
              // We need the content of the promise. Make sure it is fulfilled
              if (relationData.get('isFulfilled')) {
                // Use the fulfilled array
                relationData = relationData.get('content');
              } else {
                // If the property hasn't been fulfilled then it hasn't changed.
                // Fall back to the internal data. It contains enough for relationshipToResourceUri.
                relationData = get(record, key).mapBy('id').map(function(_id) {
                  return {id: _id};
                }) || [];
              }
            }
            
            json[key] = relationData.map(function (next){
              return this.relationshipToResourceUri(relationship, next);
            }, this);
            
          }
        }
      }
    });

    __exports__["default"] = DjangoTastypieSerializer;
  });
 global.DS.DjangoTastypieAdapter = requireModule('ember-data-tastypie-adapter')['DjangoTastypieAdapter'];
 global.DS.DjangoTastypieSerializer = requireModule('ember-data-tastypie-adapter')['DjangoTastypieSerializer'];
})(this);