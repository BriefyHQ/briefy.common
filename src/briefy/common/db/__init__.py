"""Common database classes and helpers for Briefy."""
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .model import Base  # noqa

import pytz
import sqlalchemy


def get_db(request) -> Session:
    """Return a valid DB session for the request."""
    return request.registry['db_session_factory']()

# If needed: tweaks to make new objects remains avaialble in views after being commited -
# from http://stackoverflow.com/questions/16152241


def get_engine(settings: dict) -> sqlalchemy.engine.base.Engine:
    """Return a SQLAlchemy database engine.

    :param settings: App settings
    :returns: A SQLAlchemy database engine
    """
    engine = create_engine(settings['sqlalchemy.url'], pool_recycle=3600)
    return engine


def datetime_utcnow() -> datetime:
    """Create datetime now with pytx UTC timezone.

    :return: datetime with timezone.
    """
    return datetime.now(tz=pytz.timezone('UTC'))
