from unittest import IsolatedAsyncioTestCase

from fastapi import HTTPException

from models.query_models import SearchQuery, ValidTopics, ValidCriteria
from services.search.search_service import SearchService, DualSearchService


class TestSearch(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.query = {
            "q": "Pride"
        }

    async def test_dual_search(self):
        query = SearchQuery(q="Pride")
        service = DualSearchService(query)
        results = await service.make_dual_search()
        print(results.results)
        assert not isinstance(results, HTTPException)

    async def test_fiction_search(self):
        query_model = SearchQuery(q="Pride", page=1)
        topic = ValidTopics.fiction
        service = SearchService(query_model, topic)
        await service.make_search()

    async def test_pagination_info(self):
        query_model = SearchQuery(q="Pride")
