"""AwareDateTime implementation for SQLAlchemy."""
from datetime import datetime

import pytz
import sqlalchemy.types as types


class AwareDateTime(types.TypeDecorator):
    '''Results returned as aware datetime, not naive ones.'''

    impl = types.DateTime

    def process_bind_param(self, value, dialect):
        """Always set datetime as utc."""
        data = value
        if isinstance(data, datetime) and data.tzinfo:
            utc = pytz.utc
            data = data.astimezone(utc)
        return data

    def process_result_value(self, value, dialect) -> datetime:
        """Always return a datetime with timezone information."""
        utc = pytz.utc
        return utc.localize(value)
