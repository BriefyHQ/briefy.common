"""Declarative base model to be extended by other models."""
from briefy.common.log import logger
from briefy.common.utils.transformers import json_dumps
from briefy.common.utils.transformers import to_serializable
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.orm.dynamic import AppenderQuery
from sqlalchemy.orm.query import Query

import typing as t


Attributes = t.List[str]


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

    def _actors_ids(self) -> t.List[str]:
        """List of actors ids for this object.

        :return: List of actor ids.
        """
        actors = {getattr(self, attr, None) for attr in self.__actors__}
        return list([a for a in actors if a])

    def _actors_info(self) -> dict:
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
    __raw_acl__ = ()
    __session__ = None
    __default_exclude_attributes__ = [
        '_sa_instance_state', 'request', 'versions', 'can_view_roles', 'can_list_roles',
        'can_edit_roles', 'can_create_roles', 'can_delete_roles', 'local_roles',
        'path', 'can_view', 'type'

    ]
    __colanderalchemy_config__ = {}
    __exclude_attributes__ = []
    __summary_attributes__ = []
    __summary_attributes_relations__ = []
    __listing_attributes__ = []
    __to_dict_additional_attributes__ = []

    @classmethod
    def __acl__(cls) -> t.Sequence[t.Tuple[str, str]]:
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
    def get(cls, key) -> 'Base':
        """Return one object given its primary key.

        :param key: Primary get to get this object.
        :returns: An instance of this class.
        """
        return cls.__session__.query(cls).get(key)

    @classmethod
    def _exclude_attributes(cls) -> Attributes:
        """Compute the list of attributes to be exclude from any serialization.

        :return: list of attributes to be excluded from serialization
        """
        default_set = set(cls.__default_exclude_attributes__)
        subclass_set = set(cls.__exclude_attributes__)
        return list(subclass_set.union(default_set))

    def _get_data(self, attrs: Attributes) -> dict:
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

    def _get_attrs(
            self,
            excludes: t.Optional[Attributes]=None,
            includes: t.Optional[Attributes]=None
    ) -> Attributes:
        """Ger a list of obj attrs.

        :return: A tuple containing a list of obj attrs.
        """
        excludes = excludes if excludes else []
        includes = includes if includes else []
        # use special inspect wrapper to list all attributes from the mapper class
        mapper_wrapper = inspect(self)
        all_attrs = [column.key for column in mapper_wrapper.attrs]
        for attr in includes:
            if attr not in all_attrs:
                all_attrs.append(attr)

        excludes = self._excluded_attr_from_serialization(all_attrs, excludes)
        return [key for key in all_attrs if key not in excludes]

    def _get_obj_dict_attrs(
            self,
            excludes: t.Optional[Attributes]=None,
            includes: t.Optional[Attributes]=None
    ) -> t.Tuple[dict, Attributes]:
        """Shortcut to get a copy of obj __dict__ and a list of obj attrs.

        :return: A tuple containing a copy of the obj __dict__ and a list of attrs.
        """
        attrs = self._get_attrs(excludes=excludes, includes=includes)
        data = self._get_data(attrs)
        return data, attrs

    def _excluded_attr_from_serialization(
            self,
            attrs: Attributes,
            excludes: Attributes
    ) -> Attributes:
        """Compute a list of attributes to be excluded from serialization.

        :return: List of attributes that should not be serialized.
        """
        # Add private attributes to exclusion list
        excludes.extend([key for key in attrs if key.startswith('_')])

        # use a method to compute the list of attributes to exclude
        excludes.extend(self._exclude_attributes())
        return excludes

    def _summarize_relationships(
            self,
            listing_attributes: Attributes=()
    ) -> dict:
        """Summarize relationship information.

        :return: Dictionary with summarized info for relationships.
        """
        summary_relations = self.__summary_attributes_relations__
        if listing_attributes:
            summary_relations = [item for item in summary_relations if item in listing_attributes]
        data = {}
        for key in summary_relations:
            serialized = None
            obj = getattr(self, key, None)
            if isinstance(obj, AppenderQuery):
                obj = obj.all()
            if obj and isinstance(obj, Base):
                serialized = obj.to_summary_dict()
            elif isinstance(obj, list):
                serialized = [item.to_summary_dict() for item in obj if item]
            elif isinstance(obj, dict):
                serialized = obj
            data[key] = serialized if serialized else obj
        return data

    def to_dict(
            self,
            excludes: Attributes=None,
            includes: Attributes=None
    ) -> dict:
        """Return a dictionary with fields and values used by this Class.

        :param excludes: attributes to exclude from dict representation.
        :param includes: attributes to include from dict representation.
        :returns: Dictionary with fields and values used by this Class
        """
        data = dict()
        excludes = excludes if excludes else []
        includes = includes if includes else []

        # add additional default to_dict attributes and listing attributes
        includes.extend(self.__to_dict_additional_attributes__ + self.__listing_attributes__)
        all_attrs = self._get_attrs(includes=includes, excludes=excludes)

        if isinstance(excludes, str):
            excludes = [excludes]
        if isinstance(includes, str):
            includes = [includes]

        # first get summary fields
        data.update(self._summarize_relationships(all_attrs))
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

    def update(self, values: dict):
        """Update the object with given values.

        :param values: Dictionary containing attributes and values
        :type values: dict
        """
        for k, v in values.items():
            setattr(self, k, v)

    @classmethod
    def create(cls, payload: dict) -> 'Base':
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
def json_base_model(val: Base) -> dict:
    """Base model serializer."""
    return val.to_dict()
