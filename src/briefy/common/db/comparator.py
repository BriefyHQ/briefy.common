"""Base class to create custom column comparators."""
from sqlalchemy.ext.hybrid import Comparator


class BaseComparator(Comparator):
    """Marker class to be user as base for custom comparators."""
