"""Roles defined for Briefy systems."""
from enum import Enum


class LocalRoles(Enum):
    """Assignable local roles."""

    system = 'r:system'
    customer = 'r:customer'
    professional = 'r:professional'
    project_manager = 'r:project_manager'
    scout_manager = 'r:scout_manager'
    qa_manager = 'r:qa_manager'
    finance_manager = 'r:finance_manager'
