"""Common database classes and helpers for Briefy."""

from datetime import datetime
from sqlalchemy import create_engine
from .model import Base  # noqa

import pytz


def get_db(request):
    """Return a valid DB session for the request."""
    return request.registry['db_session_factory']()

# If needed: tweaks to make new objects remains avialble in views after being commited -
# from http://stackoverflow.com/questions/16152241


def get_engine(settings):
    """Return a SQLAlchemy database engine.

    :param settings: App settings
    :type settings: dict
    :returns: A SQLAlchemy database engine
    :rtype: sqlalchemy.engine.base.Engine
    """
    engine = create_engine(settings['sqlalchemy.url'], pool_recycle=3600)
    return engine


def datetime_utcnow():
    """Create datetime now with pytx UTC timezone.
    :return: datetime with timezone.
    """
    return datetime.now(tz=pytz.timezone('UTC'))
