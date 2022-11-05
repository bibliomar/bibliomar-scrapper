from unittest import IsolatedAsyncioTestCase

from models.query_models import ValidTopics
from services.metadata.metadata_service import MetadataService


class TestMetadata(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.fiction_md5 = "C5ECB88AB0AF46661684A1D0F18A8B71"
        self.scitech_md5 = "7700D78D8BCABA3AF0EADEB4B75148C2"

    async def test_fiction_metadata(self):
        topic = ValidTopics.fiction
        service = MetadataService(self.fiction_md5, topic)
        r = await service.retrieve_metadata()

    async def test_scitech_metadata(self):
        topic = ValidTopics.scitech
        service = MetadataService(self.scitech_md5, topic)
        r = await service.retrieve_metadata()
