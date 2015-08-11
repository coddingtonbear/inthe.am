import json


class OneWaySafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            json.JSONEncoder.default(self, obj)
        except:
            return unicode(obj)
