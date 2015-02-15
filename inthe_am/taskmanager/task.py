from taskw.task import Task as TaskwTask


class Task(object):
    LIST_FIELDS = [
        'annotations',
        'blocks',
        'depends',
        'tags',
    ]
    AUTO_NULL = [
        'priority'
    ]

    def __init__(self, json=None, store=None):
        if json is None:
            taskw_task_kwargs = {}
            if store:
                taskw_task_kwargs['udas'] = store.client.config.get_udas()
            json = TaskwTask(**taskw_task_kwargs)
        self.__dict__['_json'] = json
        self.__dict__['_store'] = store

    def blocks(self):
        uuid = self._json['uuid']
        if self._store:
            blocks = self._store.client.filter_tasks({
                'depends.contains': uuid,
            })
            return [b['uuid'] for b in blocks]
        return []

    def to_taskwarrior(self, updates=None):
        task = self._json

        if updates:
            for k, v in updates.items():
                task[k] = v

        return task

    def get_json(self):
        return self._json

    def __getattr__(self, name):
        if name == '_json':
            return self.__dict__['_json']
        if name == '_store':
            return self.__dict__['_store']
        if name in self.__dict__:
            return self.__dict__[name]()
        value = self._json.get(name, None)
        if value is None and name in self.LIST_FIELDS:
            value = []
        if value is '' and name in self.AUTO_NULL:
            value = None
        return value

    def __setattr__(self, key, value):
        if key in TaskwTask.FIELDS and TaskwTask.FIELDS[key].read_only:
            return
        if value is None and key in self.LIST_FIELDS:
            value = []
        if value == '' and key in self.AUTO_NULL:
            value = None
        self.__dict__['_json'][key] = value

    def __str__(self):
        return self.__unicode__().encode('ascii', 'replace')

    def __unicode__(self):
        return self.description
