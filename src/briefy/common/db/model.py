"""Declarative base model to be extended by other models."""
from briefy.common.utils.transformers import json_dumps
from sqlalchemy.ext.declarative import declarative_base


class Base:
    """Base Declarative model."""

    __session__ = None

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
        return cls.__session_.query(cls).get(key)

    def to_dict(self):
        """Return a dictionary with fields and values used by this Class.

        :returns: Dictionary with fields and values used by this Class
        :rtype: dict
        """
        data = self.__dict__.copy()
        # Not needed for the transform
        if '_sa_instance_state' in data:
            del(data['_sa_instance_state'])
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
