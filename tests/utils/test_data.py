"""Tests for `briefy.common.utils.data` module."""
from briefy.common.utils import data
from copy import deepcopy

import pytest


testdata = [
    ('Foo', 'foo'),
    ('Foo bar', 'foo-bar'),
    ('Berlin', 'berlin'),
    (' Berlin', 'berlin'),
    (' Berlin  ', 'berlin'),
    (' Fußball  ', 'fussball'),
    (' Briefy Project in Münch  ', 'briefy-project-in-munch'),
]


@pytest.mark.parametrize('value,expected', testdata)
def test_generate_slug(value, expected):
    """Test generate_slug."""
    func = data.generate_slug
    assert func(value) == expected


testdata = [
    ({'id': '1234567890', 'title': 'Berlin'}, '12345678-berlin'),
    ({'id': '1234567890', 'title': 'Fußball'}, '12345678-fussball'),
    ({'id': '', 'title': ''}, ''),
    ({'id': None, 'title': None}, ''),
    ({'id': None, 'title': 'Fußball'}, 'fussball'),
    ({'id': '1234567890', 'title': None}, '12345678'),
    ({'id': 12345, 'title': None}, '12345'),
]


@pytest.mark.parametrize('value,expected', testdata)
def test_generate_contextual_slug(value, expected):
    """Test generate_contextual_slug."""
    func = data.generate_contextual_slug
    assert func(value) == expected


def test_objectify_works_single_dict():
    fixture = {'image': True}
    assert data.Objectify(fixture).image == fixture['image']


def test_objectify_works_single_list():
    fixture = ['image']
    assert data.Objectify(fixture)._0 == 'image'
    assert data.Objectify(fixture)._dct == fixture


def test_objectify_works_chainned_dict():
    fixture = {'image': {'type': 'pictorial', 'dimensions': [640, 480]}}
    obj = data.Objectify(fixture)
    assert isinstance(obj.image, data.Objectify)
    assert isinstance(obj._dct, dict)
    assert obj.image._dct == {'type': 'pictorial', 'dimensions': [640, 480]}
    assert obj.image.type == 'pictorial'
    assert obj.image.dimensions._0 == 640


def test_objectify_iteration_works():
    for fixture in ({'image0': 0, 'image1': 1, 'image2': 2}, [0, 1, 2]):
        contents = {0, 1, 2}
        for content in data.Objectify(fixture):
            contents.remove(content)
        assert not contents


def test_objectify_raise_attribute_error():
    fixture = {'image': True}
    obj = data.Objectify(fixture)
    with pytest.raises(AttributeError):
        obj.video


def test_objectify_customize_missing_attribute_shallow():
    fixture = {'image': True}
    obj = data.Objectify(fixture)
    obj._sentinel = None
    assert obj.video is None


def test_objectify_customize_missing_attribute_deep():
    fixture = {'image': {'type': 'pictorial', 'dimensions': [640, 480]}}
    obj = data.Objectify(fixture)
    obj._sentinel = None
    assert obj.image.dimensions.third is None


def test_objectify_dont_double_wrap():
    fixture = {'image': True}
    obj1 = data.Objectify(fixture)
    assert data.Objectify(obj1)._dct == fixture


def test_objectify_dir_works():
    fixture = {'image': True}
    obj1 = data.Objectify(fixture)
    assert dir(obj1) == sorted(['_dct', '_sentinel', 'image'])
    obj2 = data.Objectify(['anything'])
    assert dir(obj2) == sorted(['_dct', '_sentinel', '_0'])


def test_objectify_bool_works():
    fixture = {'image': True}
    assert data.Objectify(fixture)
    assert not data.Objectify({})


def test_objectify_get_works():
    fixture = {'image': True}
    assert data.Objectify(fixture)._get('image')


def test_objectify_get_empty_returns_raw():
    fixture = {'image': True}
    # Empty get should return data structure by default, but allow
    # objectify parameter to be passed as True
    assert data.Objectify(fixture)._get() == fixture
    assert data.Objectify(fixture)._get(objectify=False) == fixture
    assert data.Objectify(fixture)._get(objectify=True)._dct == fixture


def test_objectify_get_works_deep():
    fixture = {'image': {'type': 'pictorial', 'dimensions': [640, 480]}}
    obj = data.Objectify(fixture)
    assert obj._get('image.dimensions._0') == 640


def test_objectify_get_raises_attribute_error():
    fixture = {'image': {'type': 'pictorial', 'dimensions': [640, 480]}}
    obj = data.Objectify(fixture)
    with pytest.raises(AttributeError):
        obj._get('image.dimensions._3')


def test_objectify_get_works_with_default():
    fixture = {'image': {'type': 'pictorial', 'dimensions': [640, 480]}}
    obj = data.Objectify(fixture)
    # Deep path failure
    assert obj._get('image.dimensions._3', None) is None
    # Early path failure
    assert obj._get('image.other_dimensions._0', None) is None
    # raises even if obj._sentinel is set:
    with pytest.raises(AttributeError):
        obj._sentinel = None
        obj._get('image.dimensions._3')
    obj._sentinel = data.objectify_sentinel
    # Retrieves data structure
    assert obj._get('image.dimensions', objectify=False) == [640, 480]


def test_objectify_traversal():
    fixture = {
        'assignment': {
            'order': {'requirements': {'height': 480, 'exposure': '0.2s'}},
            'requirements': {'width': 640}
        },
        'requirements': {'duration': '10s', 'exposure': '1s'}
    }
    obj = data.Objectify(fixture)
    t = obj._get_traverser([
        'requirements', 'assignment.requirements', 'assignment.order.requirements'
    ])
    assert t.width == 640
    assert t.height == 480
    assert t.duration == '10s'
    assert t.exposure == '1s'


def test_objectify_deep_path_index_get():
    obj = data.Objectify({'a': {'b': 42}})
    assert obj['a.b'] == 42


def test_item_retrieval_works_with_default_value():
    obj = data.Objectify({'a': {'b': 42}})
    with pytest.raises(KeyError):
        assert obj['a.non_existent']
    obj._sentinel = 'fourty two'
    assert obj['a.non_existent'] == 'fourty two'


def test_objectify_containement_test_works_shallow_index():
    obj = data.Objectify({'a': {'b': 42}})
    assert 'a' in obj
    assert 'b' not in obj


def test_objectify_containement_test_works_deep_index():
    obj = data.Objectify({'a': {'b': 42}})
    assert 'a.b' in obj
    assert 'a.c' not in obj


def test_objectify_iterate_over_values_by_default():
    obj = data.Objectify({'a': {'b': 42}})
    iterated=  list(obj)
    assert len(iterated) == 1
    assert iterated[0]._dct == {'b': 42}


def test_objectify__keys():
    obj = data.Objectify({'a': {'b': 42}})
    assert list(obj._keys()) == ['a']


def test_objectify__values():
    obj = data.Objectify({'a': {'b': 42}})
    assert next(iter(obj._values()))._dct == {'b': 42}


def test_objectify__items():
    obj = data.Objectify({'a': {'b': 42}})
    key, value = next(iter(obj._items()))
    assert key == 'a'
    assert value._dct == {'b': 42}


def test_objectify_content_equals_other_objectify():
    fixture = {'a': {'b': 42}}
    obj1 = data.Objectify(fixture)
    obj2 = data.Objectify(deepcopy(fixture))
    assert obj1 == obj2


def test_objectify_content_equals_equivalent_mapping():
    fixture = {'a': {'b': 42}}
    obj = data.Objectify(fixture)
    assert obj == deepcopy(fixture)
