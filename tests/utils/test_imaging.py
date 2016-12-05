"""Tests for `briefy.common.utils.imaging` module."""
from briefy.common.config import THUMBOR_BASE_URL
from briefy.common.config import THUMBOR_INTERNAL_URL
from briefy.common.utils import imaging
from conftest import mock_thumbor

import httmock
import json
import os
import pytest


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

    # Generate url with spaces
    source_path = 'source/files/jobs/ _ 1234.jpg'
    assert '30x30/files/jobs/%20_%201234.jpg' in func(source_path, 30, 30, smart=False)


def test_generate_metadata_url():
    """Test generate_metadata_url."""
    func = imaging.generate_metadata_url
    source_path = 'source/files/jobs/1234.jpg'

    # URL should start with path to thumbor
    assert func(source_path, 30, 30).startswith(THUMBOR_INTERNAL_URL)

    # Generate url for image of 30x30
    assert '/meta/30x30/files/jobs/1234.jpg' in func(source_path, 30, 30)

    # Generate unsafe url
    assert 'unsafe/meta/30x30/files/jobs/1234.jpg' in func(source_path, 30, 30, signed=False)


def test_get_metadata_from_thumbor():
    """Test get_metadata_from_thumbor."""
    func = imaging.get_metadata_from_thumbor
    source_path = 'source/files/jobs/1234.jpg'

    with httmock.HTTMock(mock_thumbor):
        resp = func(source_path)

    assert resp['width'] == 5760
    assert resp['height'] == 3840
    assert isinstance(resp['raw_metadata'], dict)


def test_process_metadata():
    """Test process_metadata."""
    func = imaging.process_metadata

    data = json.load(
        open(os.path.join(__file__.rsplit('/', 1)[0], 'thumbor.json'))
    )
    raw_metadata = data['original']['metadata']
    width = data['original']['width']
    height = data['original']['height']
    size = 4059093

    metadata = func(raw_metadata, width, height, size)

    assert isinstance(metadata, dict)
    assert metadata['dimensions'] == '5760 x 3840'
    assert metadata['ratio'] == '3/2'
    assert metadata['date_time'] == '2016-06-08T16:05:33'
    assert metadata['camera_maker'] == 'Canon'
    assert metadata['camera_model'] == 'Canon EOS 5D Mark III'
    assert metadata['dpi'] == '300'
    assert metadata['shutter'] == '290241/125000'
    assert metadata['iso'] == 100
    assert metadata['exposure_time'] == '1/5'
    assert metadata['aperture'] == '126797/20000'
    assert metadata['lens_model'] == 'EF16-35mm f/2.8L II USM'
    assert metadata['orientation'] == 'Top Left'


def test_calc_scale_keep_ratio():
    """Test generate scale keeping ratio."""
    func = imaging.calc_scale_keep_ratio

    assert func((800, 600), (200, 200)) == (200, 150)
    assert func((800, 600), (300, 300)) == (300, 225)
    assert func((600, 800), (200, 200)) == (150, 200)

    with pytest.raises(ValueError):
        func((0, 0), (200, 200))

    with pytest.raises(ValueError):
        func((None, None), (200, 200))
