"""Helpers to deal with images."""
from briefy.common.config import THUMBOR_BASE_URL
from briefy.common.config import THUMBOR_INTERNAL_URL
from briefy.common.config import THUMBOR_KEY
from briefy.common.config import THUMBOR_PREFIX_SOURCE
from dateutil.parser import parse
from fractions import Fraction
from libthumbor import CryptoURL
from urllib.parse import quote

import requests


_crypto = CryptoURL(key=THUMBOR_KEY)

ORIENTATION = {
    1: 'Top Left',
    2: 'Top Right (flipped)',
    3: 'Bottom Right',
    4: 'Bottom Left (flipped)',
    5: 'Left Top (flipped)',
    6: 'Right Top',
    7: 'Right Bottom (flipped)',
    8: 'Left Bottom'
}


def _generate_thumbor_url(
        source_path: str,
        width: int,
        height: int,
        smart: bool,
        filters: tuple,
        signed: bool,
        meta: bool = False,
        internal: bool = False) -> str:
    """Generate url to an image.

    :param source_path: Relative path to the source image on S3.
    :param width: Image width, in pixels.
    :param height: Image height, in pixels.
    :param smart: Smart resizing.
    :param filters: Filters to be applied to the image.
    :param signed: Boolean indicating if we will sign this url.
    :param meta: Url should be metadata endpoint.
    :param internal: Generate an internal url.
    :return: URL
    """
    prefix = THUMBOR_BASE_URL
    if meta or internal:
        prefix = THUMBOR_INTERNAL_URL
    # Remove source prefix from source_path
    image_url = source_path.replace(THUMBOR_PREFIX_SOURCE, '')
    # Sanitize image url
    image_url = quote(image_url)
    unsafe = False if signed else True
    url = _crypto.generate(
        width=width,
        height=height,
        smart=smart,
        image_url=image_url,
        filters=filters,
        meta=meta,
        unsafe=unsafe
    )
    return '{base_url}{url}'.format(base_url=prefix, url=url)


def generate_metadata_url(
        source_path: str,
        width: int=0,
        height: int=0,
        smart: bool=False,
        signed: bool=True) -> str:
    """Generate a public url to an image.

    :param source_path: Relative path to the source image on S3.
    :param width: Image width, in pixels.
    :param height: Image height, in pixels.
    :param smart: Smart resizing.
    :param signed: Boolean indicating if we will sign this url.
    :return: URL
    """
    # Using smart resize and metadata raises an error on Thumbor
    smart = False if smart else smart
    return _generate_thumbor_url(source_path, width, height, smart, tuple(), signed, meta=True)


def generate_image_url(
        source_path: str,
        width: int=0,
        height: int=0,
        smart: bool = True,
        filters: tuple = None,
        signed: bool=True,
        internal: bool=False) -> str:
    """Generate a public url to an image.

    :param source_path: Relative path to the source image on S3.
    :param width: Image width, in pixels.
    :param height: Image height, in pixels.
    :param smart: Smart resizing.
    :param filters: Filters to be applied to this image.
    :param signed: Boolean indicating if we will sign this url.
    :param internal: Generate an internal url (to be used inside our cluster).
    :return: URL
    """
    if filters is None:
        filters = tuple()
    return _generate_thumbor_url(source_path, width, height, smart, filters, signed, internal)


def get_metadata_from_thumbor(source_path: str) -> dict:
    """Connect to briefy.thumbor to get metadata about an image.

    :param source_path: Relative path to the source image on S3.
    :return: Dictionary containing metadata information
    """
    timeout = 20  # will timeout after 20 seconds
    metadata = {
        'width': 0,
        'height': 0,
        'raw_metadata': {}
    }
    url = generate_metadata_url(source_path)
    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.Timeout:
        return metadata
    if response.status_code == 200:
        data = response.json()
        original = data.get('original', {})
        metadata['width'] = original.get('width', 0)
        metadata['height'] = original.get('height', 0)
        metadata['raw_metadata'] = original.get('metadata', {})
    return metadata


def process_metadata(raw_metadata: dict, width: int, height: int, size: int) -> dict:
    """Process raw metadata and return a dictionary with processed information.

    :param raw_metadata: Dictionary with raw metadata of an image.
    :param width: Image width.
    :param height: Image width.
    :param size: Image size.
    :param raw_metadata: Dictionary with raw metadata of an image.
    :return: dictionary with metadata.
    """
    ratio = '1'
    if width and height:
        ratio = str(Fraction(width, height))
    metadata = {
        'dimensions': '{w} x {h}'.format(w=width, h=height),
        'ratio': ratio,
        'size': size,
        'dpi': _get_dpi(raw_metadata),
        'shutter': _get_shutter(raw_metadata),
        'aperture': _get_aperture(raw_metadata),
        'iso': _get_iso(raw_metadata),
        'camera_model': _get_camera_model(raw_metadata),
        'camera_maker': _get_camera_make(raw_metadata),
        'lens_model': _get_lens_info(raw_metadata),
        'exposure_time': _get_exposure(raw_metadata),
        'orientation': _get_orientation(raw_metadata),
        'date_time': _get_date_time(raw_metadata),
    }
    return metadata


def _get_dpi(raw_metadata: dict) -> str:
    """Return dpi information extracted from metadata.

    :param raw_metadata: Dictionary with raw metadata of an image.
    :return: Formatted dpi information
    """
    default = 72
    value = ''
    try:
        resolution_x = int(raw_metadata.get(
            'Exif.Image.XResolution',
            raw_metadata.get('Exif.Photo.XResolution', default)
        ))
        resolution_y = int(raw_metadata.get(
            'Exif.Image.XResolution',
            raw_metadata.get('Exif.Photo.XResolution', default)
        ))
    except ValueError:
        resolution_x = resolution_y = default

    if resolution_x == resolution_y:
        value = '{res}'.format(res=resolution_x)
    else:
        value = '{x} / {y}'.format(x=resolution_x, y=resolution_y)
    return value


def _get_shutter(raw_metadata: dict) -> str:
    """Return shutter speed information extracted from metadata.

    :param raw_metadata: Dictionary with raw metadata of an image.
    :return: Formatted shutter speed information
    """
    value = raw_metadata.get(
            'Exif.Image.ShutterSpeedValue',
            raw_metadata.get('Exif.Photo.ShutterSpeedValue', '')
    )
    return value


def _get_aperture(raw_metadata: dict) -> str:
    """Return aperture information extracted from metadata.

    :param raw_metadata: Dictionary with raw metadata of an image.
    :return: Formatted aperture information
    """
    value = raw_metadata.get(
            'Exif.Image.ApertureValue',
            raw_metadata.get('Exif.Photo.ApertureValue', '')
    )
    return value


def _get_iso(raw_metadata: dict) -> str:
    """Return aperture information extracted from metadata.

    :param raw_metadata: Dictionary with raw metadata of an image.
    :return: Formatted iso information
    """
    value = raw_metadata.get(
            'Exif.Image.ISOSpeedRatings',
            raw_metadata.get('Exif.Photo.ISOSpeedRatings', '')
    )
    return value


def _get_camera_model(raw_metadata: dict) -> str:
    """Return camera model information extracted from metadata.

    :param raw_metadata: Dictionary with raw metadata of an image.
    :return: Formatted camera model information
    """
    value = raw_metadata.get(
            'Exif.Image.Model',
            raw_metadata.get('Exif.Photo.Model', '')
    )
    return value


def _get_camera_make(raw_metadata: dict) -> str:
    """Return camera make information extracted from metadata.

    :param raw_metadata: Dictionary with raw metadata of an image.
    :return: Formatted camera make information
    """
    value = raw_metadata.get(
            'Exif.Image.Make',
            raw_metadata.get('Exif.Photo.Make', '')
    )
    return value


def _get_exposure(raw_metadata: dict) -> str:
    """Return exposure information extracted from metadata.

    :param raw_metadata: Dictionary with raw metadata of an image.
    :return: Formatted exposure information
    """
    value = raw_metadata.get(
            'Exif.Image.ExposureTime',
            raw_metadata.get('Exif.Photo.ExposureTime', '')
    )
    return value


def _get_orientation(raw_metadata: dict) -> str:
    """Return orientation information extracted from metadata.

    http://www.impulseadventure.com/photo/exif-orientation.html
    :param raw_metadata: Dictionary with raw metadata of an image.
    :return: Formatted orientation information
    """
    value = raw_metadata.get(
            'Exif.Image.Orientation',
            raw_metadata.get('Exif.Photo.Orientation', '')
    )
    if value:
        value = ORIENTATION.get(value, value)
    return value


def _get_date_time(raw_metadata: dict) -> str:
    """Return date time information extracted from metadata.

    :param raw_metadata: Dictionary with raw metadata of an image.
    :return: Formatted date time information.
    """
    value = raw_metadata.get(
            'Exif.Image.DateTimeOriginal',
            raw_metadata.get('Exif.Photo.DateTimeOriginal', '')
    )
    try:
        value = parse(value).isoformat()
    except ValueError:
        value = ''
    return value


def _get_lens_info(raw_metadata: dict) -> str:
    """Return lens information extracted from metadata.

    :param raw_metadata: Dictionary with raw metadata of an image.
    :return: Formatted lens information.
    """
    value = raw_metadata.get(
        'Xmp.aux.Lens',
        raw_metadata.get('Exif.Photo.LensModel', '')
    )
    return value
