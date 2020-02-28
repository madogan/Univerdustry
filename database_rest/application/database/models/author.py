# -*- coding: utf-8 -*-
"""ORM Model of `author` table and related functions."""

from sqlalchemy.orm import relationship

from application import db
from application.database.mixins import ModelMixin


class Author(db.Model, ModelMixin):
    """SQLAlchemy Class of `author` table."""

    __tablename__ = "author"

    ident = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, nullable=True)
    affiliation = db.Column(db.String, default=None, nullable=True)
    cited_by = db.Column(db.Integer, default=0, nullable=True)
    cites_per_year = db.Column(db.JSON, default=None, nullable=True)
    hindex = db.Column(db.Integer, default=0, nullable=True)
    i10index = db.Column(db.Integer, default=0, nullable=True)
    interests = db.Column(db.JSON, default=None, nullable=True)
    url_picture = db.Column(db.String, nullable=True)

    # Many to many relation with `publication` table.
    # Every author has many publications. and
    # Every publication hast many authors.
    publications = relationship("Publication",
                                secondary="asc_author_publication",
                                back_populates="authors")

    _excluded_list = ["publications"]

    def __init__(self, **kwargs):
        super(Author, self).__init__(**kwargs)
