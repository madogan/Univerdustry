"""Initialization of database models.

We are importing these because we want to reach from models.

EXAMPLE:
    >>> from application.database.models.author import Author
"""
from application.database.models.author import Author
from application.database.models.publication import Publication
from application.database.models.asc_author_publication import \
    AscAuthorPublication

model_table = {
    "author": Author,
    "publication": Publication,
    "asc-author-publication": AscAuthorPublication
}
