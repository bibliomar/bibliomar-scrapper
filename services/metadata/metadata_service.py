from fastapi import Path, Query, HTTPException
from pydantic import ValidationError

from config.mysql_connection import MySQLConnect
from models.body_models import md5_reg, date_format, Metadata
from models.query_models import ValidTopics
from datetime import datetime

from services.search.search_service import SearchService


class MetadataService:

    def __init__(self, md5: str = Path(), topic: ValidTopics = Path()):
        self.md5 = md5
        self.topic = topic
        self.metadata_sql = self._sql_query_builder()
        self.placeholder_values = (md5,)

        # We will be using some static methods from the search service here.
        # Be sure to not instantiate it. We only need the static methods.
        self.search_service = SearchService

    @staticmethod
    def _datetime_to_isostr(date: datetime):

        if not isinstance(date, datetime):
            return None

        try:
            date_as_isostr = date.strftime(date_format)
        except:
            date_as_isostr = None

        return date_as_isostr

    def _metadata_as_model(self, result: dict):
        for k, v in result.items():
            if v == "":
                result[k] = None

        isbn = result.get("Identifier") or result.get("IdentifierWODASH")
        added_at = self._datetime_to_isostr(result.get("TimeAdded"))
        size = self.search_service.bytes_to_size(result.get("Filesize"))
        cover_url = self.search_service.resolve_cover_url(self.topic, result.get("Coverurl"))

        return Metadata(
            **result,
            isbn=isbn,
            topic=self.topic,
            added_at=added_at,
            size=size,
            cover_url=cover_url,
            MD5=self.md5
        )

    def _sql_query_builder(self) -> str:
        if self.topic == ValidTopics.fiction:
            columns = "Title, Author, " \
                      "Series, Edition, Language, Year, Publisher, " \
                      "Pages, Identifier, GooglebookID, ASIN, Coverurl, Extension, Filesize, TimeAdded"

            table = "fiction"
            desc_table = "fiction_description"
        else:
            columns = "Title, Author, " \
                      "Series, Edition, Language, Year, Publisher, City, VolumeInfo, " \
                      "Pages, IdentifierWODASH, GooglebookID, ASIN, Coverurl, Extension, Filesize, TimeAdded"
            table = "updated"
            desc_table = "description"

        metadata_sql = f"""SELECT {columns}, Descr from {table} as M 
        LEFT JOIN {desc_table} as D ON M.md5 = D.md5
        WHERE M.MD5 = %s"""

        return metadata_sql

    async def _find_on_database(self):
        async with MySQLConnect() as cursor:
            await cursor.execute(self.metadata_sql, args=self.placeholder_values)
            result: dict = await cursor.fetchone()
            return result

    async def retrieve_from_cache(self):
        pass

    async def retrieve_metadata(self):
        metadata = await self._find_on_database()
        # If metadata is None or an empty dict, bool(metadata) returns false.
        if not bool(metadata):
            raise HTTPException(400, "Couldn't find any file with the given MD5")

        try:
            metadata_as_model = self._metadata_as_model(metadata)
            return metadata_as_model
        except ValidationError:
            raise HTTPException(500, "Entry schema is invalid. This can be an internal issue.")
