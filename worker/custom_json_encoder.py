from flask.json import JSONEncoder
from datetime import date, datetime
from scholary import Author, Publication


class CustomJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()

        if isinstance(o, (Author, Publication)):
            return o.__dict__

        try:
            o = super(CustomJsonEncoder, self).default(o)
        except TypeError:
            o = str(o)

        return o