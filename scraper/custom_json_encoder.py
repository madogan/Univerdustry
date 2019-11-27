from flask.json import JSONEncoder
from datetime import date, datetime


class CustomJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        try:
            o = super(CustomJsonEncoder, self).default(o)
        except TypeError:
            o = str(o)

        return o