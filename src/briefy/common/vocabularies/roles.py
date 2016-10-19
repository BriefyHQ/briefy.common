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


class Groups(Enum):
    """Default groups."""

    briefy = 'g:briefy'
    bizdev = 'g:briefy_bizdev'
    finance = 'g:briefy_finance'
    mgmt = 'g:briefy_management'
    pm = 'g:briefy_pm'
    product = 'g:briefy_product'
    qa = 'g:briefy_qa'
    scout = 'g:briefy_scout'
    support = 'g:briefy_support'
    tech = 'g:briefy_tech'
    customers = 'g:customers'
    professionals = 'g:professionals'
