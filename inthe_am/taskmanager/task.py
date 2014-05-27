
class Task(object):
    def __init__(self, json, store):
        if not json:
            raise ValueError()
        self.__dict__['_json'] = json
        self.__dict__['_store'] = store

    def blocks(self):
        uuid = self._json['uuid']
        blocks = self._store.client.filter_tasks({
            'depends.contains': uuid,
        })
        return [b['uuid'] for b in blocks]

    def __getattr__(self, name):
        if name == '_json':
            return self.__dict__['_json']
        if name == '_store':
            return self.__dict__['_store']
        if name in self.__dict__:
            return self.__dict__[name]()
        return self._json.get(name, None)

    def __setattr__(self, key, value):
        self.__dict__['_json'][key] = value

    def __str__(self):
        return self.__unicode__().encode('ascii', 'replace')

    def __unicode__(self):
        return self.description
