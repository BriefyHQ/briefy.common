"""Declarative base model to be extended by other models."""
from briefy.common.utils.transformers import json_dumps
from briefy.common.utils.transformers import to_serializable
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm.query import Query


class Security:
    """Security mixin to be applied to all SQLAlchemy classes."""

    __actors__ = ()
    __raw_acl__ = (
        ('list', ()),
        ('view', ()),
        ('edit', ()),
        ('delete', ()),
    )

    def _actors_ids(self) -> list:
        """List of actors ids for this object.

        :return: List of actor ids.
        """
        actors = {getattr(self, attr, None) for attr in self.__actors__}
        return list([a for a in actors if a])

    def _actors_info(self) -> list:
        """Return actor information for this object.

        :return: Dictionary with attr name and user id.
        """
        return {attr: getattr(self, attr, None) for attr in self.__actors__}

    @hybrid_method
    def _can_list(self, user: 'briefy.ws.auth.AuthenticatedUser') -> bool:
        """Check if the user can list this object.

        :param id: User object..
        :return: Boolean indicating if user is allowed to list this object.
        """
        user_id = getattr(user, 'id')
        user_groups = set(getattr(user, 'groups'))
        acl = dict(self.__raw_acl__)
        allowed = set(acl.get('list', []))
        if user_groups.intersection(allowed):
            return True
        else:
            return self.is_actor(user_id)


    @hybrid_method
    def is_actor(self, user_id: str) -> bool:
        """Check if the user_id is an actor in this object.

        :param id: UUID of an user.
        :return: Check if this id is for a user in here.
        """
        return user_id in [str(u) for u in self._actors_ids()]


class Base(Security):
    """Base Declarative model."""

    __session__ = None
    __exclude_attributes__ = ['_sa_instance_state', 'request']
    __summary_attributes__ = []
    __listing_attributes__ = []

    @classmethod
    def query(cls) -> Query:
        """Return query object.

        :returns: A query object
        """
        return cls.__session__.query(cls)

    @classmethod
    def get(cls, key):
        """Return one object given its primary key.

        :param key: Primary get to get this object.
        :returns: An instance of this class.
        """
        return cls.__session__.query(cls).get(key)

    def _get_obj_dict_attrs(self) -> tuple:
        """Shortcut to get a copy of obj __dict__ and a list of obj attrs.

        :return: A tuple containing a copy of the obj __dict__ and a list of attrs.
        """
        data = self.__dict__.copy()
        attrs = [key for key in data.keys()]
        return (data, attrs)

    def _excluded_attr_from_serialization(self, attrs: list, excludes: list) -> list:
        """Compute a list of attributes to be excluded from serialization.

        :return: List of attributes that should not be serialized.
        """
        # Add private attributes to exclusion list
        excludes.extend([key for key in attrs if key.startswith('_')])

        # Add class level excluded attributes
        excludes.extend(
            list(self.__exclude_attributes__)
        )
        return excludes

    def _to_dict(self, data: dict, attrs: list, excludes: list, required: list) -> dict:
        """Return a dictionary with fields and values used by this Class.

        :param data: A copy of object __dict__.
        :param attrs: List of object attributes.
        :param excludes: attributes to exclude from dict representation.
        :param required: List of explicitly required attributes.
        :returns: Dictionary with fields and values used by this Class
        """
        excludes = self._excluded_attr_from_serialization(attrs, excludes)

        for attr in excludes:
            if attr in data:
                del(data[attr])

        for attr in required:
            if attr not in data:
                data[attr] = getattr(self, attr)
        return data

    def to_dict(self, excludes: list=None) -> dict:
        """Return a dictionary with fields and values used by this Class.

        :param excludes: attributes to exclude from dict representation.
        :returns: Dictionary with fields and values used by this Class
        """
        data, attrs = self._get_obj_dict_attrs()
        excludes = excludes if excludes else []
        if isinstance(excludes, str):
            excludes = [excludes]
        data = self._to_dict(data, attrs, excludes, [])
        return data

    def to_summary_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        data, attrs = self._get_obj_dict_attrs()
        excludes = []
        summary_attributes = self.__summary_attributes__
        summary_attributes = summary_attributes if summary_attributes else []
        # Remove attributes not on the summary_attributes
        if summary_attributes:
            excludes = [key for key in attrs if key not in summary_attributes]

        data = self._to_dict(data, attrs, excludes, required=summary_attributes)
        return data

    def to_listing_dict(self) -> dict:
        """Return a listing-ready version of the dict representation of this Class.

        Used to serialize this object for listings.
        :returns: Dictionary with fields and values used by this Class
        """
        data, attrs = self._get_obj_dict_attrs()
        excludes = []

        listing_attributes = self.__listing_attributes__
        listing_attributes = listing_attributes if listing_attributes else []

        # Remove attributes not on the listing_attributes
        if listing_attributes:
            excludes = [key for key in attrs if key not in listing_attributes]

        data = self._to_dict(data, attrs, excludes, required=listing_attributes)
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
