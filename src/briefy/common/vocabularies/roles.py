"""Roles defined for Briefy systems."""
from briefy.common.vocabularies import LabeledEnum


options = [
    ('system', 'system', 'r:system'),
    ('customer', 'customer', 'r:customer'),
    ('professional', 'professional', 'r:professional'),
    ('project_manager', 'project_manager', 'r:project_manager'),
    ('scout_manager', 'scout_manager', 'r:scout_manager'),
    ('qa_manager', 'qa_manager', 'r:qa_manager'),
    ('finance_manager', 'finance_manager', 'r:finance_manager'),
    ('owner', 'owner', 'r:owner'),
]


LocalRolesChoices = LabeledEnum('LocalRolesChoices', options)


options = [
    ('briefy', 'g:briefy', 'g:briefy'),
    ('bizdev', 'g:briefy_bizdev', 'g:briefy_bizdev'),
    ('finance', 'g:briefy_finance', 'g:briefy_finance'),
    ('mgmt', 'g:briefy_management', 'g:briefy_management'),
    ('pm', 'g:briefy_pm', 'g:briefy_pm'),
    ('product', 'g:briefy_product', 'g:briefy_product'),
    ('qa', 'g:briefy_qa', 'g:briefy_qa'),
    ('scout', 'g:briefy_scout', 'g:briefy_scout'),
    ('system', 'g:system', 'g:system'),
    ('support', 'g:briefy_support', 'g:briefy_support'),
    ('tech', 'g:briefy_tech', 'g:briefy_tech'),
    ('customers', 'g:customers', 'g:customers'),
    ('professionals', 'g:professionals', 'g:professionals')
]


Groups = LabeledEnum('Groups', options)
