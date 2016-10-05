"""Image mixin."""
from briefy.common.utils import imaging
from collections.abc import Sequence
from decimal import Decimal
from sqlalchemy_utils import JSONType

import sqlalchemy as sa


class Image:
    """A mixin providing image information."""

    _image_filters = (
        ('maxbytes', (int,)),
        ('quality', (int,)),
        ('format', (str,)),
        ('saturation', (Decimal,)),
        ('no_upscale', tuple()),
    )

    _available_sizes = (
        ('thumb', 150, 150),
        ('preview', 1200, 800),
        ('original', 0, 0)
    )

    source_path = sa.Column(sa.String(1000), nullable=False)
    filename = sa.Column(sa.String(1000), nullable=False)
    content_type = sa.Column(sa.String(100), nullable=False, default='image/jpeg')
    size = sa.Column(sa.Integer, default=0)
    width = sa.Column(sa.Integer, default=0)
    height = sa.Column(sa.Integer, default=0)
    raw_metadata = sa.Column(JSONType)

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
        for name, width, height in self._available_sizes:
            download_url = imaging.generate_image_url(
                self.source_path,
                width=width,
                height=height,
                smart=True
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
