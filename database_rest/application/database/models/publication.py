# -*- coding: utf-8 -*-
"""ORM Model of `publication` table and related functions."""

from sqlalchemy.orm import relationship

from application import db
from application.database.mixins import ModelMixin


class Publication(db.Model, ModelMixin):
    """SQLAlchemy Class of `publication` table."""

    __tablename__ = "publication"

    ident = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=True)
    url = db.Column(db.String, nullable=True)
    source_url = db.Column(db.String, nullable=True)
    raw_content = db.Column(db.String, nullable=True)
    content_text = db.Column(db.String, nullable=True)
    cited_by = db.Column(db.Integer, default=0, nullable=True)

    # Many to many relation with `author` table.
    # Every author has many publications. and
    # Every publication hast many authors.
    authors = relationship("Author", secondary="asc_author_publication",
                           back_populates="publications")

    _excluded_list = ["authors"]

    def __init__(self, **kwargs):
        super(Publication, self).__init__(**kwargs)
