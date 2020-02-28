# -*- coding: utf-8 -*-
"""ORM Model of `asc_author_publication` table."""

from application import db
from application.database.mixins import ModelMixin


class AscAuthorPublication(db.Model, ModelMixin):
    __tablename__ = "asc_author_publication"

    author_id = db.Column("author_id",
                          db.ForeignKey("author.ident",
                                        ondelete="cascade",
                                        onupdate="cascade"),
                          primary_key=True)

    publication_id = db.Column("publication_id",
                               db.ForeignKey("publication.ident",
                                             ondelete="cascade",
                                             onupdate="cascade"),
                               primary_key=True)

    def __init__(self, **kwargs):
        super(AscAuthorPublication, self).__init__(**kwargs)
