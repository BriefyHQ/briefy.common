"""Tests if JSON serialization overriding is applied."""
import json
import briefy.common


def test_json_can_serialize_uuid():
    import uuid
    a = [uuid.uuid4()]
    assert json.dumps(a)


def test_json_can_serialize_datetime():
    import datetime
    a = [datetime.datetime.now()]
    assert json.dumps(a)


def test_json_can_serialize_objectify():
    from briefy.common.utils.data import Objectify
    a = [Objectify({'b': 1})]
    b = json.dumps(a)
    assert json.loads(b) == {'b': 1}
