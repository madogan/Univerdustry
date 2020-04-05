# -*- coding: utf-8 -*-
"""This module consists custom json encoder class."""
from datetime import date, datetime

from bson import json_util, ObjectId
from flask.json import JSONEncoder
from pymongo.cursor import Cursor


class CustomJsonEncoder(JSONEncoder):
    """This class updates json encoder of application."""

    def default(self, o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()

        if isinstance(o, bytes):
            return str(o)

        if isinstance(o, ObjectId):
            return str(o)

        if isinstance(o, Cursor):
            return [dict(i) for i in o]

        try:
            o = json_util.default(o)
        except TypeError:
            o = str(o)

        return o
