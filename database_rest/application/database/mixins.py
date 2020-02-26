# -*- coding: utf-8 -*-
"""The model mixin is general class for database models.

There are some same operation_table for every model. This class reduce code
lines. Also, it enables dictionary like operation_table.
"""

import datetime

from worker import db
from sqlalchemy import inspect


class ModelMixin:
    """This class generic database class for repeated operation_table."""

    def __init__(self, *args, **kwargs):
        super(ModelMixin, self).__init__(*args, **kwargs)

    def __getitem__(self, key):
        """This function enable dictionary like indexing.
        
        Arguments:
            key: Attribute of class.

        Returns:
            Value of attribute.
        """
        if key not in getattr(self, "_excluded_list", []):
            return getattr(self, key)

    def keys(self):
        """Returns database model object keys in list."""
        keys = inspect(self).attrs.keys()
        return [key for key in keys
                if key not in getattr(self, "_excluded_list", [])]

    def items(self):
        """Returns database model object keys and values as list of tuples."""
        items = inspect(self).attrs.items()
        return [(key, val) for key, val in items
                if key not in getattr(self, "_excluded_list", [])]

    def save(self, commit=True):
        db.session.add(self)

        if commit:
            db.session.commit()

    def delete(self, commit=True):
        db.session.delete(self)

        if commit:
            db.session.commit()

    @classmethod
    def update(cls, ident, data, commit=True):
        if getattr(cls, "updated_at", None):
            data["updated_at"] = datetime.datetime.now()

        if "ident" in data:
            del data["ident"]

        # noinspection PyUnresolvedReferences
        db.session.query(cls) \
            .filter(cls.ident == ident) \
            .update(data)

        if commit is True:
            # Commit changes.
            db.session.commit()

    @classmethod
    def get_columns(cls):
        columns = cls.__table__.columns
        return (getattr(cls, col) for col in columns)

    @classmethod
    def get_attributes(cls, required: bool = False,
                       include_ident: bool = False):
        """Returns attributes of class.

        Arguments:
            required: If it is True returns only required attributes
                for model. (not null for database convention)
            include_ident: If it is True add ``ident`` name of primary key
                for all models.
        
        Returns:
            :obj:`list` of :obj:`str`: List of string as attributes
                of model class.
        """
        columns = cls.__table__.columns

        if required is True:
            columns = [col.name for col in columns
                       if not col.nullable and "ident" != col.name]
        else:
            columns = [col.name for col in columns if "ident" != col.name]

        if include_ident is True:
            columns.append("ident")

        return columns

    def __repr__(self):
        return f"<{self.__class__.__name__}({getattr(self, 'ident', None)})>"
