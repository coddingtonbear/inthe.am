import copy
import datetime

import dateutil
import pytz


class Task(object):
    DATE_FIELDS = [
        'due', 'entry', 'modified', 'start', 'wait', 'scheduled',
    ]
    LIST_FIELDS = [
        'annotations', 'tags',
    ]
    READ_ONLY_FIELDS = [
        'id', 'uuid', 'urgency', 'entry', 'modified', 'imask',
        'resource_uri', 'start', 'status',
    ]
    STRING_FIELDS = [
        'depends', 'description', 'project', 'priority',
    ]
    KNOWN_FIELDS = DATE_FIELDS + LIST_FIELDS + STRING_FIELDS

    def __init__(self, json, taskrc=None, store=None):
        if not json:
            raise ValueError()
        self.json = json
        self.taskrc = taskrc
        self.store = store

    @staticmethod
    def get_timezone(tzname, offset):
        if tzname is not None:
            return pytz.timezone(tzname)
        static_timezone = pytz.tzinfo.StaticTzInfo()
        static_timezone._utcoffset = datetime.timedelta(
            seconds=offset
        )
        return static_timezone

    def get_json(self):
        return self.json

    def get_safe_json(self):
        return {
            k: v for k, v in self.json.items()
            if k not in self.READ_ONLY_FIELDS
            and k in self.KNOWN_FIELDS
        }

    @classmethod
    def from_serialized(cls, data):
        data = copy.deepcopy(data)
        for key in data:
            if key in cls.DATE_FIELDS and data[key]:
                data[key] = dateutil.parser.parse(
                    data[key],
                    tzinfos=cls.get_timezone
                )
            elif key in cls.LIST_FIELDS and data[key] is None:
                data[key] = []
        return Task(data)

    def _date_from_taskw(self, value):
        value = datetime.datetime.strptime(
            value,
            '%Y%m%dT%H%M%SZ',
        )
        return value.replace(tzinfo=pytz.UTC)

    def _date_to_taskw(self, value):
        raise NotImplementedError()

    def __getattr__(self, name):
        if name == 'udas':
            if not self.taskrc:
                value = None
            else:
                value = {}
                defined_udas = self.taskrc.get_udas()
                for uda, definition in defined_udas.items():
                    if uda not in self.get_json():
                        continue
                    value[uda] = {
                        'label': definition['label'],
                        'value': self.get_json()[uda],
                    }
            return value
        if name == 'blocks' and self.store:
            uuid = self.json['uuid']
            blocks = self.store.client.filter_tasks({
                'depends.contains': uuid,
            })
            return ','.join([
                v['uuid'] for v in blocks
            ])

        try:
            return self.json[name]
        except KeyError:
            raise AttributeError()

    @property
    def id(self):
        return self.json['id'] if self.json['id'] else None

    @property
    def urgency(self):
        return float(self.json['urgency']) if self.json['urgency'] else None

    def __str__(self):
        return self.__unicode__().encode('ascii', 'replace')

    def __unicode__(self):
        return self.description
