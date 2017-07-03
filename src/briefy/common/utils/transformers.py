"""Helpers to transform data."""
from briefy.common.utils.data import Objectify
from enum import Enum
from functools import singledispatch
from typing import Any

import colander
import datetime
import json


HAS_SQLALCHEMY_UTILS = True
try:
    from sqlalchemy_utils import Country
    from sqlalchemy_utils import PhoneNumber
except ImportError:
    HAS_SQLALCHEMY_UTILS = False


@singledispatch
def to_serializable(val) -> str:
    """Used by default."""
    return str(val)


@to_serializable.register(datetime.datetime)
def ts_datetime(val: datetime.datetime) -> str:
    """Used if *val* is an instance of datetime."""
    return val.isoformat()


@to_serializable.register(datetime.date)
def ts_date(val: datetime.date) -> str:
    """Used if *val* is an instance of date."""
    return '{value}T00:00:00'.format(value=val.isoformat())


@to_serializable.register(datetime.time)
def ts_time(val: datetime.time) -> str:
    """Used if *val* is an instance of time."""
    return val.isoformat()


@to_serializable.register(colander._null)
def ts_colander_null(val: colander._null) -> None:
    """Used if *val* is an instance of colander Null."""
    return None


if HAS_SQLALCHEMY_UTILS:
    @to_serializable.register(Country)
    def ts_sautils_country(val: Country) -> str:
        """Serialize Country instance do country code string."""
        return val.code

    @to_serializable.register(PhoneNumber)
    def ts_sautils_phonenumber(val: PhoneNumber) -> str:
        """Serialize PhoneNumber instance to number string."""
        return str(val.international)


@to_serializable.register(Enum)
def ts_labeled_enum(val: Enum) -> str:
    """Serialize LabeledEnum instance to string."""
    return str(val.value)


@to_serializable.register(Objectify)
def ts_labeled_enum(val: Objectify) -> str:
    """Serialize LabeledEnum instance to string."""
    return val._get()


def json_dumps(obj: Any) -> str:
    """Transform an obj to a JSON representation."""
    return json.dumps(obj, default=to_serializable)
