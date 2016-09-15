"""Helpers to deal with images."""
from briefy.common.config import THUMBOR_BASE_URL
from briefy.common.config import THUMBOR_INTERNAL_URL
from briefy.common.config import THUMBOR_KEY
from briefy.common.config import THUMBOR_PREFIX_SOURCE
from libthumbor import CryptoURL

import requests


_crypto = CryptoURL(key=THUMBOR_KEY)


def _generate_thumbor_url(
        source_path: str,
        width: int,
        height: int,
        smart: bool,
        signed: bool,
        meta: bool = False) -> str:
    """Generate url to an image.

    :param source_path: Relative path to the source image on S3.
    :param width: Image width, in pixels.
    :param height: Image height, in pixels.
    :param smart: Smart resizing.
    :param signed: Boolean indicating if we will sign this url.
    :param meta: Url should be metadata endpoint.
    :return: URL
    """
    prefix = THUMBOR_BASE_URL
    if meta:
        prefix = THUMBOR_INTERNAL_URL
    # Remove source prefix from source_path
    image_url = source_path.replace(THUMBOR_PREFIX_SOURCE, '')
    unsafe = False if signed else True
    url = _crypto.generate(
        width=width,
        height=height,
        smart=smart,
        image_url=image_url,
        meta=meta,
        unsafe=unsafe
    )
    return '{base_url}{url}'.format(base_url=prefix, url=url)


def generate_metadata_url(
        source_path: str,
        width: int=0,
        height: int=0,
        smart: bool = True,
        signed: bool=True) -> str:
    """Generate a public url to an image.

    :param source_path: Relative path to the source image on S3.
    :param width: Image width, in pixels.
    :param height: Image height, in pixels.
    :param smart: Smart resizing.
    :param signed: Boolean indicating if we will sign this url.
    :return: URL
    """
    return _generate_thumbor_url(source_path, width, height, smart, signed, meta=True)


def generate_image_url(
        source_path: str,
        width: int=0,
        height: int=0,
        smart: bool = True,
        signed: bool=True) -> str:
    """Generate a public url to an image.

    :param source_path: Relative path to the source image on S3.
    :param width: Image width, in pixels.
    :param height: Image height, in pixels.
    :param smart: Smart resizing.
    :param signed: Boolean indicating if we will sign this url.
    :return: URL
    """
    return _generate_thumbor_url(source_path, width, height, smart, signed)


def get_metadata_from_thumbor(source_path: str) -> dict:
    """Connect to briefy.thumbor to get metadata about an image.

    :param source_path: Relative path to the source image on S3.
    :return: Dictionary containing metadata information
    """
    metadata = {
        'width': 0,
        'height': 0,
        'raw_metadata': {}
    }
    url = generate_metadata_url(source_path)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        original = data.get('original', {})
        metadata['width'] = original.get('width', 0)
        metadata['height'] = original.get('height', 0)
        metadata['raw_metadata'] = original.get('metadata', {})
    return metadata
