# -*- coding: utf-8 -*-
"""This module consists custom json encoder class."""

from flask.json import JSONEncoder
from datetime import date, datetime

from worker.database.mixins import ModelMixin


class CustomJsonEncoder(JSONEncoder):
    """ This class updates json encoder of application.
    
    :datetime:`date`and :datetime:`datetime` class are not implemented for
    serialization.
    We add how to serialize this type of objects.
    """
    def default(self, o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()

        if isinstance(o, bytes):
            return str(o)

        if isinstance(o, ModelMixin):
            return dict(o)

        if isinstance(o, list) and isinstance(o[0], ModelMixin):
            return [dict(i) for i in o]

        try:
            o = super(CustomJsonEncoder, self).default(o)
        except TypeError:
            o = str(o)

        return o
