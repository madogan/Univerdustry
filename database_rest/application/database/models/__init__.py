"""Initialization of database models.

We are importing these because we want to reach from models.

EXAMPLE:
    >>> from worker.database.models.author import Author
"""
from worker.database.models.author import Author
from worker.database.models.publication import Publication
from worker.database.models.asc_author_publication import \
    AscAuthorPublication

model_table = {
    "author": Author,
    "publication": Publication,
    "asc-author-publication": AscAuthorPublication
}
