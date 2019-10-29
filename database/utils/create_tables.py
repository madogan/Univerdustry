import sqlalchemy as sql
import sqlalchemy.dialects.postgresql as sql_pg

from config import DEFAULT_PROFILE_IMAGE_URL
from sqlalchemy.ext.declarative import declarative_base


try:
    # TODO: Parameteres will be gotten from env variables.
    # TODO: Search best practice for database password for security.
    engine = sql.create_engine("postgresql://univerdustry:univerdustry@localhost/univerdustry", echo=True)
except Exception as e:
    # TODO: Find appropriate exception class.
    print(f"Engine creation error.\n\nError: {str(e)}")


# Base databas model class declarations.
Base = declarative_base()


class Author(Base):
    __tablename__ = "author"

    # Ident will come from Google Scholar ID of authors.
    # Also, Google Scholar IDs are 12 chars.
    ident = sql.Column(sql.String(12), primary_key=True)
    name = sql.Column(sql.String, unique=True, nullable=False)
    affiliation = sql.Column(sql.String, nullable=False)
    university_domain = sql.Column(sql.String, nullable=False)
    interests = sql.Column(sql_pg.JSONB, nullable=True)
    cited_by_count = sql.Column(sql.Integer, default=0)
    h_index = sql.Column(sql.Integer, default=0)
    i10_index = sql.Column(sql.Integer, default=0)
    url_picture = sql.Column(sql.String, default=DEFAULT_PROFILE_IMAGE_URL)


class Paper(Base):
    __tablename__ = "paper"

    ident = sql.Column(sql.String(12), primary_key=True)
    title = sql.Column(sql.String, nullable=False)
    publicated_at = sql.Column(sql.DateTime, nullable=False)
    url = sql.Column(sql.String, nullable=True)
    eprint = sql.Column(sql.String, nullable=True)
    cited_by_count = sql.Column(sql.Integer, default=0)
    raw_paper = sql.Column(sql_pg.BYTEA, nullable=True)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
