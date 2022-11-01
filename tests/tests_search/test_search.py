from unittest import IsolatedAsyncioTestCase

from models.query_models import SearchQuery, ValidTopics, ValidCriteria
from services.search.search_service import SearchService


class TestSearch(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.query = {
            "q": "Pride"
        }

    async def test_fiction_search(self):
        query_model = SearchQuery(q="Pride")
        topic = ValidTopics.fiction
        service = SearchService(query_model, topic)

    async def test_pagination_info(self):
        query_model = SearchQuery(q="Pride")
