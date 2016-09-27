"""Tests for `briefy.common.utils.imaging` module."""
from briefy.common.config import THUMBOR_BASE_URL
from briefy.common.config import THUMBOR_INTERNAL_URL
from briefy.common.utils import imaging
from conftest import mock_thumbor

import httmock


def test_generate_image_url():
    """Test generate_image_url."""
    func = imaging.generate_image_url
    source_path = 'source/files/jobs/1234.jpg'

    # URL should start with path to thumbor unless we set it as internal
    assert func(source_path, 30, 30).startswith(THUMBOR_BASE_URL)
    assert func(source_path, 30, 30, internal=True).startswith(THUMBOR_INTERNAL_URL)

    # Generate url for image of 30x30
    assert '30x30/smart/files/jobs/1234.jpg' in func(source_path, 30, 30)

    # Generate url for image of 1x1
    assert '1x1/smart/files/jobs/1234.jpg' in func(source_path, 1, 1)

    # Generate url for image of 30x30, without smart cropping
    assert '30x30/files/jobs/1234.jpg' in func(source_path, 30, 30, smart=False)

    # Generate unsafe url
    assert 'unsafe/30x30/smart/files/jobs/1234.jpg' in func(source_path, 30, 30, signed=False)

    # Adding filters to the image
    filters = (
        'maxbytes(4000000)',
        'brightness(40)',
    )
    url = func(source_path, 30, 30, filters=filters)
    assert 'filters' in url
    assert 'maxbytes(4000000)' in url
    assert 'brightness(40)' in url

    # Passing no filters
    filters = tuple()
    url = func(source_path, 30, 30, filters=filters)
    assert 'filters' not in url

    filters = None
    url = func(source_path, 30, 30, filters=filters)
    assert 'filters' not in url

    url = func(source_path, 30, 30)
    assert 'filters' not in url


def test_generate_metadata_url():
    """Test generate_metadata_url."""
    func = imaging.generate_metadata_url
    source_path = 'source/files/jobs/1234.jpg'

    # URL should start with path to thumbor
    assert func(source_path, 30, 30).startswith(THUMBOR_INTERNAL_URL)

    # Generate url for image of 30x30
    assert '/meta/30x30/smart/files/jobs/1234.jpg' in func(source_path, 30, 30)

    # Generate unsafe url
    assert 'unsafe/meta/30x30/smart/files/jobs/1234.jpg' in func(source_path, 30, 30, signed=False)


def test_get_metadata_from_thumbor():
    """Test get_metadata_from_thumbor."""
    func = imaging.get_metadata_from_thumbor
    source_path = 'source/files/jobs/1234.jpg'

    with httmock.HTTMock(mock_thumbor):
        resp = func(source_path)

    assert resp['width'] == 5760
    assert resp['height'] == 3840
    assert isinstance(resp['raw_metadata'], dict)
