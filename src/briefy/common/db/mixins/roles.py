"""Roles mixins."""
from sqlalchemy_utils import UUIDType

import colander
import sqlalchemy as sa


class BriefyRoles:
    """A Mixin providing internal Briefy roles for an object."""

    _project_manager = sa.Column(
        'project_manager',
        UUIDType(binary=False),
        info={'colanderalchemy': {
              'title': 'Project Manager',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )

    _finance_manager = sa.Column(
        'finance_manager',
        UUIDType(binary=False),
        info={'colanderalchemy': {
              'title': 'Finance Manager',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )

    _scout_manager = sa.Column(
        'scout_manager',
        UUIDType(binary=False),
        info={'colanderalchemy': {
              'title': 'Scout Manager',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )

    _qa_manager = sa.Column(
        'qa_manager',
        UUIDType(binary=False),
        info={'colanderalchemy': {
              'title': 'QA Manager',
              'validator': colander.uuid,
              'missing': colander.drop,
              'typ': colander.String}}
    )

    @property
    def project_manager(self) -> str:
        """Return the project_manager id for this object.

        :return: ID of the project_manager.
        """
        return self._project_manager

    @project_manager.setter
    def project_manager(self, value: str):
        """Set a new project_manager for this object.

        :param value: ID of the project_manager.
        """
        self._project_manager = value

    @property
    def finance_manager(self) -> str:
        """Return the finance_manager id for this object.

        :return: ID of the finance_manager.
        """
        return self._finance_manager

    @finance_manager.setter
    def finance_manager(self, value: str):
        """Set a new finance_manager for this object.

        :param value: ID of the finance_manager.
        """
        self._finance_manager = value

    @property
    def scout_manager(self) -> str:
        """Return the scout_manager id for this object.

        :return: ID of the scout_manager.
        """
        return self._scout_manager

    @scout_manager.setter
    def scout_manager(self, value: str):
        """Set a new scout_manager for this object.

        :param value: ID of the scout_manager.
        """
        self._scout_manager = value

    @property
    def qa_manager(self) -> str:
        """Return the qa_manager id for this object.

        :return: ID of the qa_manager.
        """
        return self._qa_manager

    @qa_manager.setter
    def qa_manager(self, value: str):
        """Set a new qa_manager for this object.

        :param value: ID of the qa_manager.
        """
        self._qa_manager = value
