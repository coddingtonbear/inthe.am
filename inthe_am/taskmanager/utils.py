import datetime
import json
import re
import shlex


UUID_FINDER = re.compile(
    r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
)


class OneWaySafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime(
                "%Y%m%dT%H%M%SZ"
            )

        try:
            json.JSONEncoder.default(self, obj)
        except:
            return unicode(obj)


def shlex_without_quotes(value):
    lex = shlex.shlex(value)
    lex.quotes = '"'
    lex.whitespace_split = True
    return list(lex)


def get_uuids_from_string(value):
    return UUID_FINDER.findall(value)
