"""Helpers to transform data."""
from functools import singledispatch
from sqlalchemy_utils import Country

import colander
import datetime
import json


@singledispatch
def to_serializable(val):
    """Used by default."""
    return str(val)


@singledispatch
def to_serializable_none(val):
    """Used by default."""
    return str(val)


@to_serializable.register(datetime.datetime)
def ts_datetime(val):
    """Used if *val* is an instance of datetime."""
    return val.isoformat()


@to_serializable.register(datetime.date)
def ts_date(val):
    """Used if *val* is an instance of date."""
    return '{}T00:00:00'.format(val.isoformat())


@to_serializable.register(datetime.time)
def ts_time(val):
    """Used if *val* is an instance of time."""
    return val.isoformat()


@to_serializable.register(colander._null)
def ts_colander_null(val):
    """Used if *val* is an instance of colander Null."""
    return None


@to_serializable.register(Country)
def ts_sautils_country(val):
    """Serialize Country instance do country code string."""
    return val.code


def json_dumps(obj):
    """Transform an obj to a JSON representation."""
    return json.dumps(obj, default=to_serializable)
