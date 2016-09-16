"""Image mixin."""
from briefy.common.utils import imaging
from sqlalchemy_utils import JSONType

import sqlalchemy as sa


class Image:
    """A mixin providing image information."""

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
        """Generate a dictionary with processed metadata information

        :returns: A dictionary containing metadata information.
        """
        metadata = {
            'aperture': '',
            'iso': '',
            'shutter': ''
        }
        raw_metadata = self.raw_metadata
        if raw_metadata:
            metadata['aperture'] = raw_metadata.get('Exif.Photo.ApertureValue', '')
            metadata['iso'] = raw_metadata.get('Exif.Photo.ISOSpeedRatings', '')
            metadata['shutter'] = raw_metadata.get('Exif.Photo.ShutterSpeedValue', '')
        return metadata

    @property
    def image(self) -> dict:
        """Generate a dictionary with image information

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
