import json
import shlex


class OneWaySafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            json.JSONEncoder.default(self, obj)
        except:
            return unicode(obj)


def shlex_without_quotes(value):
    lex = shlex.shlex(value)
    lex.quotes = '"'
    lex.whitespace_split = True
    return list(lex)
