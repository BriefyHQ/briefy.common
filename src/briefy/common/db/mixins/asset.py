"""Image mixin."""
from briefy.common.utils import imaging
from collections.abc import Sequence
from decimal import Decimal
from sqlalchemy.dialects.postgresql import JSONB

import logging
import sqlalchemy as sa


logger = logging.getLogger(__name__)


class Asset:
    """Mixin for an Asset.

    An Asset is a deliverable content of a Job.
    It is subclassed to specific types like Image and Video.
    """

    source_path = sa.Column(sa.String(1000), nullable=False)
    """Path to the source file.

    i.e.: files/foo/bar/image.jpg
    """

    filename = sa.Column(sa.String(1000), nullable=False)
    """Original filename of the source file.

    i.e.: image.jpg
    """

    content_type = sa.Column(sa.String(100), nullable=False)
    """Mimetype of the file.

    i.e.: image/jpeg
    """

    size = sa.Column(sa.Integer, default=0)
    """Filesize, in bytes.

    i.e.: 4000000
    """
    width = sa.Column(sa.Integer, default=0)
    """File width, in pixels.

    i.e.: 4096
    """

    height = sa.Column(sa.Integer, default=0)
    """File height, in pixels.

    i.e.: 2048
    """

    raw_metadata = sa.Column(JSONB)
    """Raw metadata from the source file.

    Dictionary containing information extracted from file's metadata.
    """


class ImageMixin:
    """A mixin providing base image methods."""

    _image_filters = (
        ('maxbytes', (int,)),
        ('quality', (int,)),
        ('fill', (str,)),
        ('format', (str,)),
        ('saturation', (Decimal,)),
        ('no_upscale', tuple()),
    )
    """Available filters to be applied to the source image."""

    _available_sizes = (
        # ('name'. (w, h), keep_ratio, smart, fit-in),
        ('thumb', (150, 150), False, True, False),
        ('thumb_nocrop', (150, 150), False, False, True),
        ('preview', (1200, 800), False, False, False),
        ('original', (0, 0), False, False, False)  # As there is no resize, no need to keep ratio
    )
    """Available sizes to image crop and resizing.

    Format is:

        * ('size name'. (width, height), keep_ratio, smart, fit-in)

    """

    @property
    def image_filters(self) -> dict:
        """Return the available image filters.

        :return: Dictionary with filters
        """
        return dict(self._image_filters)

    def update_metadata(self) -> bool:
        """Update metadata about the source image from Thumbor.

        :returns: Status of the update
        """
        status = False
        source_path = self.source_path
        if not source_path:
            return status
        data = imaging.get_metadata_from_thumbor(self.source_path)
        if data['width'] != 0 and hasattr(self, 'update'):
            # Using update method available on Base
            self.update(data)
            status = True
        return status

    @property
    def metadata_(self) -> dict:
        """Generate a dictionary with processed metadata information.

        :returns: A dictionary containing metadata information.
        """
        raw_metadata = self.raw_metadata
        raw_metadata = raw_metadata if raw_metadata else {}
        metadata = imaging.process_metadata(
            raw_metadata, self.width, self.height, self.size
        )
        return metadata

    @property
    def image(self) -> dict:
        """Generate a dictionary with image information.

        :returns: A dictionary containing image information.
        """
        download_url = imaging.generate_image_url(
            self.source_path,
            smart=False
        )
        image = {
            'size': self.size,
            'width': self.width,
            'height': self.height,
            'download': download_url,
            'scales': self.scales
        }
        return image

    @property
    def scales(self) -> dict:
        """Generate a mapping of scales for this image.

        :return: A dictionary containing image scales.
        """
        scales = {}
        for name, dimensions, ratio, smart, fit_in in self._available_sizes:
            filters = []
            width, height = dimensions
            if fit_in:
                filters.append('fill(white)')
            if ratio:
                try:
                    original = (self.width, self.height)
                    width, height = imaging.calc_scale_keep_ratio(original, dimensions)
                except ValueError:
                    logger.exception(
                        '{repr}: {original} could not be resized to {dimensions}'.format(
                            repr=self,
                            original=original,
                            dimensions=dimensions
                        )
                    )

            download_url = imaging.generate_image_url(
                self.source_path,
                width=width,
                height=height,
                filters=tuple(filters),
                smart=smart,
                fit_in=fit_in
            )
            scales[name] = {
                'width': width if width else self.width,
                'height': height if height else self.height,
                'download': download_url
            }
        return scales

    def scale_with_filters(
            self,
            width: int=0,
            height: int=0,
            filters: tuple=tuple(),
            smart: bool=False,
            internal: bool=False
    ) -> dict:
        """Generate scale info for this image, given width, height and a tuple of filters.

        :param width: Width of the scale. Use 0 for original size.
        :param height: Height of the scale. Use 0 for original size.
        :param filters: Tuple of filters in the format ('filter_id', (param1. param2))
        :param smart: Smart image processing.
        :param internal: Generate an internal url.
        :return: Scale information with width, height and download url.
        """
        allowed_filters = self.image_filters
        processed = []
        for filter in filters:
            filter_id, params = filter
            if filter_id not in allowed_filters:
                # TODO: Log this cases
                raise ValueError('Invalid filter_id')
            if not isinstance(params, Sequence):
                # TODO: Check params
                raise ValueError('Params should be a Sequence')
            processed.append(
                '{filter_id}({params})'.format(
                    filter_id=filter_id,
                    params=','.join(['{0}'.format(p) for p in params])
                )
            )
        download_url = imaging.generate_image_url(
            self.source_path,
            width=width,
            height=height,
            filters=tuple(processed),
            smart=smart,
            internal=internal
        )
        image = {
            'width': width if width else self.width,
            'height': height if height else self.height,
            'download': download_url
        }
        return image


class Image(ImageMixin, Asset):
    """An Image object.

    It subclasses :class:`Asset` and :class:`ImageMixin`.
    """

    pass


class ThreeSixtyImageMixin:
    """A 360 Image object.

    It will provide specific actions to deal with this type of assets.
    """

    pass


class ThreeSixtyImage(ThreeSixtyImageMixin, Image):
    """A 360 Image object.

    It subclasses :class:`Image` and :class:`ThreeSixtyImageMixin`.
    """

    pass


class VideoMixin:
    """A mixin providing video specific-information."""

    duration = sa.Column(sa.Integer, default=0)
    """Duration of this video, in seconds.

    i.e.: 60
    """

    codecs = sa.Column(sa.Text, default='')
    """Codecs used in this video."""

    audio_channels = sa.Column(sa.Integer, default=0)
    """Number of audio channels."""


class Video(VideoMixin, Asset):
    """A Video object.

    It subclasses :class:`Asset` and :class:`VideoMixin`.
    """

    pass
