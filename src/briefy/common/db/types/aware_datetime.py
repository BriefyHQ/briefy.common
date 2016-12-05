"""AwareDateTime implementation for SQLAlchemy."""
from datetime import datetime

import pytz
import sqlalchemy.types as types


class AwareDateTime(types.TypeDecorator):
    """Type that guarantees datetime will be on UTC on the server.

    Results returned as aware datetime, not naive ones.
    """

    impl = types.DateTime

    def process_bind_param(self, value, dialect) -> datetime:
        """Save datetime value as UTC."""
        data = value
        if isinstance(data, datetime) and data.tzinfo:
            utc = pytz.utc
            data = data.astimezone(utc)
        return data

    def process_result_value(self, value, dialect) -> datetime:
        """Return datetime value as UTC."""
        utc = pytz.utc
        if value:
            return utc.localize(value)
