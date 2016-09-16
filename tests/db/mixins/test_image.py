"""Test Image mixin."""
from briefy.common.db import Base
from briefy.common.db.mixins import Image
from briefy.common.db.mixins import Mixin
from conftest import DBSession
from conftest import mock_thumbor

import httmock
import pytest


data = {
    'updated_at': '2016-09-08T15:36:28.087123Z',
    'source_path': 'source/files/jobs/1234.jpg',
    'height': 3840,
    'width': 5760,
    'size': 4049867,
    'content_type': 'image/jpeg',
    'filename': '1234.jpg',
    'raw_metadata': {
            'Exif.Image.Copyright': 'Cyril Folliot Photographe',
            'Exif.Image.DateTime': '2016-06-13T14:15:15',
            'Exif.Image.ExifTag': '254',
            'Exif.Image.Make': 'Canon',
            'Exif.Image.Model': 'Canon EOS 5D Mark III',
            'Exif.Image.ResolutionUnit': 2,
            'Exif.Image.Software': 'Adobe Photoshop Lightroom 6.6 (Macintosh)',
            'Exif.Image.XResolution': '300',
            'Exif.Image.YResolution': '300',
            'Exif.Photo.ApertureValue': '126797/20000',
            'Exif.Photo.BodySerialNumber': '423023000017',
            'Exif.Photo.ColorSpace': 1,
            'Exif.Photo.CustomRendered': 0,
            'Exif.Photo.DateTimeDigitized': '2016-06-08T16:05:33',
            'Exif.Photo.DateTimeOriginal': '2016-06-08T16:05:33',
            'Exif.Photo.ExifVersion': '0230',
            'Exif.Photo.ExposureBiasValue': '0',
            'Exif.Photo.ExposureMode': 0,
            'Exif.Photo.ExposureProgram': 3,
            'Exif.Photo.ExposureTime': '1/5',
            'Exif.Photo.FNumber': '9',
            'Exif.Photo.Flash': 16,
            'Exif.Photo.FocalLength': '16',
            'Exif.Photo.FocalPlaneResolutionUnit': 3,
            'Exif.Photo.FocalPlaneXResolution': '1600',
            'Exif.Photo.FocalPlaneYResolution': '1600',
            'Exif.Photo.ISOSpeedRatings': 100,
            'Exif.Photo.LensModel': 'EF16-35mm f/2.8L II USM',
            'Exif.Photo.LensSerialNumber': '0000807363',
            'Exif.Photo.LensSpecification': [
                '16',
                '35',
                '0',
                '0'
            ],
            'Exif.Photo.MaxApertureValue': '3',
            'Exif.Photo.MeteringMode': 5,
            'Exif.Photo.RecommendedExposureIndex': '100',
            'Exif.Photo.SceneCaptureType': 0,
            'Exif.Photo.SensitivityType': 2,
            'Exif.Photo.ShutterSpeedValue': '290241/125000',
            'Exif.Photo.SubSecTimeDigitized': '00',
            'Exif.Photo.SubSecTimeOriginal': '00',
            'Exif.Photo.WhiteBalance': 0,
            'Iptc.Application2.Copyright': [
                'Cyril Folliot Photographe'
            ],
            'Iptc.Application2.DateCreated': [
                '2016-06-08'
            ],
            'Iptc.Application2.DigitizationDate': [
                '2016-06-08'
            ],
            'Iptc.Application2.DigitizationTime': [
                '16:05:33+00:00'
            ],
            'Iptc.Application2.RecordVersion': [
                4
            ],
            'Iptc.Application2.TimeCreated': [
                '16:05:33+00:00'
            ],
            'Iptc.Envelope.CharacterSet': [
                '\u001b%G'
            ],
            'Xmp.aux.ApproximateFocusDistance': '163/100',
            'Xmp.aux.Firmware': '1.3.3',
            'Xmp.aux.FlashCompensation': '0/1',
            'Xmp.aux.ImageNumber': '0',
            'Xmp.aux.Lens': 'EF16-35mm f/2.8L II USM',
            'Xmp.aux.LensID': '246',
            'Xmp.aux.LensInfo': '16/1 35/1 0/0 0/0',
            'Xmp.aux.LensSerialNumber': '0000807363',
            'Xmp.aux.SerialNumber': '423023000017',
            'Xmp.dc.format': [
                'image',
                'jpeg'
            ],
            'Xmp.dc.rights': {
                'x-default': 'Cyril Folliot Photographe'
            },
            'Xmp.xmp.CreatorTool': 'Adobe Photoshop Lightroom 6.6 (Macintosh)',
            'Xmp.xmp.MetadataDate': '2016-06-13T14:15:15+02:00',
            'Xmp.xmp.ModifyDate': '2016-06-13T14:15:15+02:00',
            'Xmp.xmp.Rating': 1,
            'Xmp.xmpMM.DerivedFrom/stRef:documentID':
            'xmp.did:cac0ab20-7d44-4d98-8bdf-62d899a63b43',
            'Xmp.xmpMM.DerivedFrom/stRef:instanceID':
            'xmp.iid:cac0ab20-7d44-4d98-8bdf-62d899a63b43',
            'Xmp.xmpMM.DerivedFrom/stRef:originalDocumentID': 'E52405F8BAB69C2D9E59FF708047A67E',
            'Xmp.xmpMM.DocumentID': 'xmp.did:99ae046a-6721-426e-aa6e-617ed80cdb3b',
            'Xmp.xmpMM.History': [],
            'Xmp.xmpMM.History[1]': '',
            'Xmp.xmpMM.History[1]/stEvt:action': 'derived',
            'Xmp.xmpMM.History[1]/stEvt:parameters':
            'converted from image/x-canon-cr2 to image/jpeg',
            'Xmp.xmpMM.History[2]': '',
            'Xmp.xmpMM.History[2]/stEvt:action': 'saved',
            'Xmp.xmpMM.History[2]/stEvt:changed': '/',
            'Xmp.xmpMM.History[2]/stEvt:instanceID': 'xmp.iid:cac0ab20-7d44-4d98-8bdf-62d899a63b43',
            'Xmp.xmpMM.History[2]/stEvt:softwareAgent': 'Adobe Photoshop Lightroom 6.6 (Macintosh)',
            'Xmp.xmpMM.History[2]/stEvt:when': '2016-06-13T14:15:15+02:00',
            'Xmp.xmpMM.History[3]': '',
            'Xmp.xmpMM.History[3]/stEvt:action': 'converted',
            'Xmp.xmpMM.History[3]/stEvt:parameters': 'from image/jpeg to image/x-canon-cr2',
            'Xmp.xmpMM.History[4]': '',
            'Xmp.xmpMM.History[4]/stEvt:action': 'derived',
            'Xmp.xmpMM.History[4]/stEvt:parameters':
            'converted from image/x-canon-cr2 to image/jpeg',
            'Xmp.xmpMM.History[5]': '',
            'Xmp.xmpMM.History[5]/stEvt:action': 'saved',
            'Xmp.xmpMM.History[5]/stEvt:changed': '/',
            'Xmp.xmpMM.History[5]/stEvt:instanceID': 'xmp.iid:99ae046a-6721-426e-aa6e-617ed80cdb3b',
            'Xmp.xmpMM.History[5]/stEvt:softwareAgent': 'Adobe Photoshop Lightroom 6.6 (Macintosh)',
            'Xmp.xmpMM.History[5]/stEvt:when': '2016-06-13T14:15:15+02:00',
            'Xmp.xmpMM.InstanceID': 'xmp.iid:99ae046a-6721-426e-aa6e-617ed80cdb3b',
            'Xmp.xmpMM.OriginalDocumentID': 'E52405F8BAB69C2D9E59FF708047A67E'
    },
    'id': '7c229be5-a5e0-4fb5-a0a6-8a9ff499aa5d',
    'created_at': '2016-09-08T15:36:28.087112Z'
}


class ImageAsset(Image, Mixin, Base):
    """An Image asset."""

    __tablename__ = 'images'
    __session__ = DBSession


@pytest.mark.usefixtures("db_transaction")
class TestImageMixin:
    """Test ImageMixin database model."""

    def _get_or_create_asset(self, session):
        """Create an image asset."""
        asset = session.query(ImageAsset).first()
        if not asset:
            asset = ImageAsset(**data)
            session.add(asset)
            session.commit()
            session.flush()
        return asset

    def test_create_image_asset(self, session):
        """Create a image asset instance."""
        asset = self._get_or_create_asset(session)

        assert isinstance(asset, ImageAsset)

    def test_image(self, session):
        """Test image property."""
        asset = self._get_or_create_asset(session)

        image_data = asset.image
        assert isinstance(image_data, dict)
        assert 'files/jobs/1234.jpg' in image_data['download']
        assert image_data['width'] == 5760
        assert image_data['height'] == 3840
        assert isinstance(image_data['scales'], dict)

    def test_scales(self, session):
        """Test scales property."""
        asset = self._get_or_create_asset(session)

        scales_data = asset.scales
        assert isinstance(scales_data, dict)

        assert 'original' in scales_data
        assert scales_data['original']['width'] == 5760
        assert scales_data['original']['height'] == 3840
        assert 'smart/files/jobs/1234.jpg' in scales_data['original']['download']

        assert 'thumb' in scales_data
        assert scales_data['thumb']['width'] == 150
        assert scales_data['thumb']['height'] == 150
        assert '150x150/smart/files/jobs/1234.jpg' in scales_data['thumb']['download']

        assert 'preview' in scales_data
        assert scales_data['preview']['width'] == 1200
        assert scales_data['preview']['height'] == 800
        assert '1200x800/smart/files/jobs/1234.jpg' in scales_data['preview']['download']

    def test_update_metadata(self, session):
        """Test update_metadata method."""
        asset = self._get_or_create_asset(session)
        asset.width = 0
        asset.height = 0
        asset.raw_metadata = {}

        with httmock.HTTMock(mock_thumbor):
            asset.update_metadata()

        assert asset.width == 5760
        assert asset.height == 3840
        assert asset.raw_metadata['Exif.Image.Make'] == 'Canon'

    def test_metadata(self, session):
        """Test metadata property."""
        asset = self._get_or_create_asset(session)

        metadata = asset.metadata_
        assert metadata['aperture'] == '126797/20000'
        assert metadata['iso'] == 100
        assert metadata['shutter'] == '290241/125000'
