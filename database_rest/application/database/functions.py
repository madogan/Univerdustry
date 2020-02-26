# -*- coding: utf-8 -*-
"""Functions those necessary for some database operation table."""

import os
import json

from worker import logger
from flask import json, current_app
from sqlalchemy.engine import create_engine
from worker.utils.contextor import ensure_app_context
from sqlalchemy_utils.functions.database import (database_exists,
                                                 create_database)


def check_database_tables(db_table_name: str):
    """Check a Table Exists

    Arguments:
        db_table_name: Name of db table.
    """
    url = current_app.config.get("SQLALCHEMY_DATABASE_URI")

    if url is None:
        raise ValueError("Database URL can not be None.")

    engine = create_engine(url, json_serializer=json.dumps)
    return engine.dialect.has_table(engine, db_table_name)


def check_database(url: str = None) -> bool:
    """Check existence of database according to url.

    Args:
        url: Database url string."

    Returns:
        :obj:`bool`: True, database exists.
    """
    if url is None:
        url = current_app.config.get("SQLALCHEMY_DATABASE_URI")

    if url is None:
        raise ValueError("Database URL can not be None.")

    return database_exists(url)


@ensure_app_context
def init_db():
    """This function creates database and tables if does not exist."""
    from worker import db
    from flask_migrate import migrate, init, upgrade

    if not check_database():
        url = current_app.config.get("SQLALCHEMY_DATABASE_URI")

        if url is None:
            raise ValueError("Database URL can not be None.")

        create_database(url, encoding="utf-8")

    if not os.path.exists(os.path.join("application", "migrations")):
        db.create_all()
        init(directory=os.path.join("application", "migrations"))

    migrate(directory=os.path.join("application", "migrations"))

    upgrade(directory=os.path.join("application", "migrations"))

    logger.debug('Init DB done!')
