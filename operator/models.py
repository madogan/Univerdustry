import os

import sqlalchemy.dialects.postgresql as sql_pg

from sqlalchemy.orm import relationship

from app import db


class AscAuthorPublication(db.Model):
    __tablename__ = "asc_author_publication"

    author_id = db.Column('author_id', db.String, db.ForeignKey('author.ident'), primary_key=True)
    publication_id = db.Column('publication_id', db.String, db.ForeignKey('publication.ident'), primary_key=True)


class Author(db.Model):
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
    url_picture = db.Column(db.String, nullable=True,
                            default=os.getenv("DEFAULT_PROFILE_IMAGE_URL"))

    # Many to many relation with `publication` table.
    # Every author has many publications. and
    # Every publication hast many authors.
    publications = relationship("Publication", secondary="AscAuthorPublication", back_populates="authors")


class Publication(db.Model):
    __tablename__ = "publication"

    ident = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=True)
    url = db.Column(db.String, default="", nullable=True)
    source_url = db.Column(db.String, default="", nullable=True)
    raw_content = db.Column(sql_pg.BYTEA, default=None, nullable=True)
    content_text = db.Column(db.String, default=None, nullable=True)
    cited_by = db.Column(db.Integer, default=0, nullable=True)

    # Many to many relation with `author` table.
    # Every author has many publications. and
    # Every publication hast many authors.
    authors = relationship("Author", secondary="AscAuthorPublication", back_populates="publications")
