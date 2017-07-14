"""Declarative base model to be extended by other models."""
from briefy.common.log import logger
from briefy.common.utils.transformers import json_dumps
from briefy.common.utils.transformers import to_serializable
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.query import Query


class Security:
    """Security mixin to be applied to all SQLAlchemy classes."""

    __actors__ = ()
    __raw_acl__ = (
        ('create', ()),
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
    def is_actor(self, user_id: str) -> bool:
        """Check if the user_id is an actor in this object.

        :param id: UUID of an user.
        :return: Check if this id is for a user in here.
        """
        return user_id in [str(u) for u in self._actors_ids()]


class Base(Security):
    """Base Declarative model."""

    __parent_attr__ = None
    __additional_can_view_lr__ = []
    __session__ = None
    __exclude_attributes__ = [
        '_sa_instance_state', 'request', 'versions', 'path', 'can_view', 'type', 'local_roles'
    ]
    __summary_attributes__ = []
    __summary_attributes_relations__ = []
    __listing_attributes__ = []

    @classmethod
    def __acl__(cls) -> tuple:
        """Return a tuple of pyramid ACLs based on __raw_acl__ attribute."""
        result = dict()
        for permission, roles in cls.__raw_acl__:
            for role_id in roles:
                if role_id not in result:
                    result[role_id] = [permission]
                else:
                    result[role_id].append(permission)
        return tuple([(key, value) for key, value in result.items()])

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

    def _get_data(self, attrs) -> dict:
        """Ger a map of obj with all data from attrs.

        :return: A map containing all data from obj attrs.
        """
        data = {}
        for attr in attrs:
            try:
                value = getattr(self, attr)
            except AttributeError as error:
                logger.error(
                    'Attribute not found in model {name}. Error: {error}'.format(
                        error=error,
                        name=self.__class__.__name__
                    )
                )
            else:
                if isinstance(value, InstrumentedList):
                    new_list = []
                    for item in value:
                        new_list.append(item)
                    value = new_list
                data[attr] = value
        return data

    def _get_attrs(self, excludes=None, includes=None) -> list:
        """Ger a list of obj attrs.

        :return: A tuple containing a list of obj attrs.
        """
        excludes = excludes if excludes else []
        includes = includes if includes else []

        all_attrs = list(self.__dict__.keys())
        for attr in includes:
            if attr not in all_attrs:
                all_attrs.append(attr)

        excludes = self._excluded_attr_from_serialization(all_attrs, excludes)
        return [key for key in all_attrs if key not in excludes]

    def _get_obj_dict_attrs(self, excludes=(), includes=()) -> tuple:
        """Shortcut to get a copy of obj __dict__ and a list of obj attrs.

        :return: A tuple containing a copy of the obj __dict__ and a list of attrs.
        """
        attrs = self._get_attrs(excludes=excludes, includes=includes)
        data = self._get_data(attrs)
        return data, attrs

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
        for attr in excludes:
            if attr in data:
                del(data[attr])

        for attr in required:
            if attr not in data:
                data[attr] = getattr(self, attr)
        return data

    def _summarize_relationships(self, listing_attributes=()) -> dict:
        """Summarize relationship information.

        :return: Dictionary with summarized info for relationships.
        """
        summary_relations = self.__summary_attributes_relations__
        if listing_attributes:
            summary_relations = [item for item in summary_relations if item in listing_attributes]
        data = {}
        for key in summary_relations:
            obj = getattr(self, key, None)
            if obj is None:
                serialized = None
            elif isinstance(obj, Base):
                serialized = obj.to_summary_dict()
            else:
                serialized = [item.to_summary_dict() for item in obj if item]
            data[key] = serialized
        return data

    def to_dict(self, excludes: list=None, includes: list=None) -> dict:
        """Return a dictionary with fields and values used by this Class.

        :param excludes: attributes to exclude from dict representation.
        :param includes: attributes to include from dict representation.
        :returns: Dictionary with fields and values used by this Class
        """
        data = dict()
        excludes = excludes if excludes else []
        includes = includes if includes else []

        if isinstance(excludes, str):
            excludes = [excludes]
        if isinstance(includes, str):
            includes = [includes]

        # first get summary fields
        data.update(self._summarize_relationships())
        # now get all the other fields but excluding summary fields
        excludes.extend(list(data.keys()))
        # get data and attrs
        obj_data, attrs = self._get_obj_dict_attrs(
            excludes=excludes,
            includes=includes
        )
        data.update(obj_data)
        return data

    def to_summary_dict(self) -> dict:
        """Return a summarized version of the dict representation of this Class.

        Used to serialize this object within a parent object serialization.
        :returns: Dictionary with fields and values used by this Class
        """
        data = {}
        excludes = []
        summary_attributes = self.__summary_attributes__
        summary_attributes = summary_attributes if summary_attributes else []
        data.update(self._summarize_relationships(summary_attributes))

        # get all attrs list
        attrs = self._get_attrs(includes=summary_attributes)
        # Remove attributes not on the summary_attributes
        if summary_attributes:
            excludes = [key for key in attrs if key not in summary_attributes]

        # also add to excludes all already summarized fields
        summary_excludes = list(data.keys())
        excludes.extend(summary_excludes)

        # now get attrs list obj_data and update data payload
        obj_data, attrs = self._get_obj_dict_attrs(
            excludes=excludes,
            includes=summary_attributes
        )
        data.update(obj_data)
        return data

    def to_listing_dict(self) -> dict:
        """Return a listing-ready version of the dict representation of this Class.

        Used to serialize this object for listings.
        :returns: Dictionary with fields and values used by this Class
        """
        data = {}
        listing_attributes = self.__listing_attributes__
        listing_attributes = listing_attributes if listing_attributes else []
        data.update(self._summarize_relationships(listing_attributes))
        attrs = self._get_attrs(includes=listing_attributes)
        # Remove attributes not on the listing_attributes
        excludes = []
        if listing_attributes:
            excludes = [key for key in attrs if key not in listing_attributes]

        # also add to excludes all already summarized fields
        summary_excludes = list(data.keys())
        excludes.extend(summary_excludes)

        # now get attrs list obj_data and update data payload
        obj_data, attrs = self._get_obj_dict_attrs(
            excludes=excludes,
            includes=listing_attributes
        )
        data.update(obj_data)
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

    @classmethod
    def create(cls, payload) -> object:
        """Factory that creates a new instance of this object.

        :param payload: Dictionary containing attributes and values
        :type payload: dict
        """
        obj = cls(**payload)
        session = obj.__session__
        session.add(obj)
        session.flush()
        return obj


Base = declarative_base(cls=Base)


@to_serializable.register(Base)
def json_base_model(val):
    """Base model serializer."""
    return val.to_dict()
