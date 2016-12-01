"""Tests for `briefy.common.vocabularies.roles` module."""
from briefy.common.vocabularies import roles

def test_local_roles():
    """Test local roles vocabulary."""
    vocab = roles.LocalRoles

    assert len(vocab) == 7
    assert vocab['system'].value == 'r:system'
    assert vocab['system'].name == 'system'


def test_groups():
    """Test local roles vocabulary."""
    vocab = roles.Groups

    assert len(vocab) == 13
    assert vocab['professionals'].value == 'g:professionals'
    assert vocab['professionals'].name == 'professionals'
