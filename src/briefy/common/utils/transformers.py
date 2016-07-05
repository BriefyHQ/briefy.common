"""Helpers to transform data."""
import datetime
import decimal
import json


class EnhancedJSONEncoder(json.JSONEncoder):
    """JSON Encoder that deals with additional types."""

    def default(self, obj):
        """Default encoder."""
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return '{}T00:00:00'.format(obj.isoformat())
        elif isinstance(obj, datetime.time):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return str(obj)
        else:
            return super().default(obj)


def json_dumps(obj):
    """Transform an obj to a JSON representation."""
    return json.dumps(obj, cls=EnhancedJSONEncoder)
