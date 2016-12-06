"""Tests for `briefy.common.vocabularies.roles` module."""
from briefy.common.vocabularies import roles


def test_local_roles():
    """Test local roles vocabulary."""
    vocab = roles.LocalRolesChoices

    assert len(vocab) == 8
    assert vocab['system'].value == 'system'
    assert vocab['system'].name == 'system'
    assert vocab['system'].label == 'r:system'


def test_groups():
    """Test local roles vocabulary."""
    vocab = roles.Groups

    assert len(vocab) == 13
    assert vocab['professionals'].value == 'g:professionals'
    assert vocab['professionals'].name == 'professionals'
