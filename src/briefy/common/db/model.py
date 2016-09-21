"""Declarative base model to be extended by other models."""
from briefy.common.utils.transformers import json_dumps
from briefy.common.utils.transformers import to_serializable
from sqlalchemy.ext.declarative import declarative_base


class Base:
    """Base Declarative model."""

    __session__ = None
    __exclude_attributes__ = ['_sa_instance_state', 'request']

    @classmethod
    def query(cls):
        """Return query object.

        :returns: A query object
        :rtype: sqlalchemy.query
        """
        return cls.__session__.query(cls)

    @classmethod
    def get(cls, key):
        """Return one object given its primary key.

        :param key: Tuple (country, code, address_id)
        :type key: tuple
        :returns: An Object
        :rtype: object
        """
        return cls.__session__.query(cls).get(key)

    def to_dict(self, excludes=None):
        """Return a dictionary with fields and values used by this Class.

        :param excludes: attributes to exclude from dict representation.
        :type excludes: list
        :returns: Dictionary with fields and values used by this Class
        :rtype: dict
        """
        data = self.__dict__.copy()
        excludes = list(excludes or [])
        default_excludes = getattr(self, '__exclude_attributes__', None)
        excludes.extend(default_excludes or [])
        for attr in excludes:
            if attr in data:
                del(data[attr])
        return data

    def to_JSON(self):
        """Return a JSON string with the object representation.

        :returns: JSON string with the object representation
        :rtype: str
        """
        data = self.to_dict()
        return json_dumps(data)

    def update(self, values):
        """Update the object with given values.

        :param values: Dictionary containing attributes and values
        :type values: dict
        """
        for k, v in values.items():
            setattr(self, k, v)

Base = declarative_base(cls=Base)


@to_serializable.register(Base)
def json_base_model(val):
    """Base model serializer."""
    return val.to_dict()
