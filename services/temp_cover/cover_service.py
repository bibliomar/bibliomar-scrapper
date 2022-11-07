import logging

from aioredis import RedisError
from fastapi import HTTPException
from fastapi.params import Query, Path
from grab_fork_from_libgen import AIOMetadata
from grab_fork_from_libgen.exceptions import MetadataError
from grab_fork_from_libgen.search_config import get_request_headers
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession, HTMLResponse, Element
from requests import exceptions

from config.redis_connection import RedisConnection
from models.query_models import ValidTopics
from services.search.search_service import SearchService


class TempCoverService:

    """
    A temporary solution for temp_cover scraping since Z-Library is now offline.
    Only works if you are allowed to hotlink covers by the libgen team.
    Adds a new step before using grab-fork-from-libgen temp_cover scraping.
    """

    def __init__(self, md5: str = Path(...), topic: ValidTopics = Path(...)):
        self.logger = logging.getLogger("biblioterra")
        self.md5 = md5
        self.topic = topic
        self.timeout = 30
        self.metadata = AIOMetadata(self.timeout)
        self.libgen_base = "https://libgen.is"

    async def _get_cover_with_library(self):
        try:
            cover_url = await self.metadata.get_cover(self.md5)
            return cover_url
        except MetadataError as e:
            raise HTTPException(400, e)

    @staticmethod
    async def _is_md5_invalid(response: HTMLResponse):
        try:
            html = response.html
            html_ele: Element = html.find("html")[0]
            html_text = html_ele.full_text
            if html_text.find("No record with such MD5 hash has been found") != -1:
                return True
            return False
        except (KeyError, TypeError, AttributeError, ValueError) as e:
            print(e)
            return True

    async def save_on_cache(self, result: str):
        expires = SearchService.expires_in(168)

        try:
            async with RedisConnection() as redis:
                await redis.set(f"{self.md5}-{self.topic}-temp_cover", result, ex=expires)

        except RedisError as e:
            print(e)

    async def retrieve_from_cache(self) -> str | None:
        try:
            async with RedisConnection() as redis:
                possible_cache = await redis.get(f"{self.md5}-{self.topic}-temp_cover")
                return possible_cache

        except RedisError:
            return None

    async def get_cover(self):

        session = AsyncHTMLSession()

        if self.topic == ValidTopics.scitech:
            topic_url = "/book/index.php?md5="
        else:
            topic_url = "/fiction/"

        req_url = self.libgen_base + topic_url + self.md5

        error_on_main = False
        page: HTMLResponse | None = None

        try:
            page: HTMLResponse = await session.get(req_url, headers=get_request_headers(),
                                                   timeout=self.timeout)

        except (exceptions.Timeout, exceptions.ConnectionError, exceptions.HTTPError):
            error_on_main = True
        if page is None:
            error_on_main = True
        if await self._is_md5_invalid(page):
            raise HTTPException(400, "No record with such MD5 hash has been found.")

        if not error_on_main:
            soup = BeautifulSoup(page.html.raw_html, "html.parser")
            img_select = soup.select_one("img")
            if img_select is None:
                pass
            else:
                try:
                    img_src = img_select["src"]
                    cover_url = self.libgen_base + img_src
                    return cover_url
                except KeyError as e:
                    pass

        return await self._get_cover_with_library()
