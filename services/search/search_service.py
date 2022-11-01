import json
import math

from aioredis import RedisError
from fastapi import HTTPException, Depends, Path
from pydantic import ValidationError, BaseModel

from pymysql.err import Error
from hurry.filesize import size, alternative
from config.mysql_connection import MySQLConnect
from config.redis_connection import RedisConnection
from models.body_models import SearchEntry, CoverInfo
from models.query_models import ValidTopics, SearchQuery, ValidCriteria
from models.response_models import SearchPaginationInfo, SearchResponse


class SQLData(BaseModel):
    search_sql: str
    pagination_sql: str
    placeholder_values: list


class SearchService:
    """
    This is the improved search service that makes queries directly to a mysql database.
    """

    def __init__(self, search_params: SearchQuery = Depends(), topic: ValidTopics = Path(...)):
        self.topic = topic
        self.query = search_params

        sql_handler = self._sql_query_builder()
        self.search_sql = sql_handler.search_sql
        self.pagination_sql = sql_handler.pagination_sql
        self.placeholder_values = sql_handler.placeholder_values

        self.libgen_fiction_base = "https://libgen.is/fictioncovers"
        self.libgen_scitech_base = "https://libgen.is/covers"
        self.libgenrocks_fiction_base = "https://libgen.rocks/fictioncovers"
        self.libgenrocks_scitech_base = "https://libgen.rocks/covers"

    @staticmethod
    def _bytes_to_size(size_to_convert: int | str):
        if size_to_convert is None or int(size_to_convert) == 0:
            return "0 B"
        return size(int(size_to_convert), system=alternative)

    @staticmethod
    def expires_in(hours: int):

        if hours is None:
            hours = 4
        # 3600 seconds is equivalent to 1 hour.
        return hours * 3600

    def _sql_query_builder(self) -> SQLData:

        if self.topic is ValidTopics.fiction:
            table = "fiction"
        else:
            table = "updated"

        query_criteria = self.query.criteria
        if query_criteria is None or query_criteria == ValidCriteria.any:
            if self.topic == ValidTopics.scitech:
                # This is a FULLTEXT index on "updated" (non-fiction) table that covers most relevant columns.
                sql_criteria = "Title, Author, Series, Publisher, Year, Periodical, VolumeInfo"
            else:
                sql_criteria = "Title, Author, Series"
        else:
            sql_criteria = self.query.criteria

        search_sql = f"""
        SELECT MD5, Title, Author, Language, Extension, Filesize, Coverurl from {table} 
        WHERE MATCH( {sql_criteria} ) AGAINST(%s) AND MD5 != '' AND Title != '' AND Author != ''
        """

        pagination_sql = f"""
        SELECT COUNT(*) from {table} 
        WHERE MATCH( {sql_criteria} ) AGAINST(%s) AND MD5 != '' AND Title != '' AND Author != ''
        """

        placeholder_values = [self.query.q]

        lang = self.query.language
        _format = self.query.format

        if lang:
            lang_sql = """ 
            AND Language = %s
            """
            search_sql += lang_sql
            pagination_sql += lang_sql

            placeholder_values.append(lang)

        if _format:
            _format_sql = """ 
            AND Extension = %s
            """
            search_sql += _format_sql
            pagination_sql += _format_sql

            placeholder_values.append(_format)

        if self.query.page == 1:
            offset = 0
        else:
            offset = (self.query.page - 1) * 10
        limit_end = offset + 25

        # Only adds LIMIT to search sql
        search_sql += f"""
        LIMIT {offset},{limit_end}
        """

        return SQLData(search_sql=search_sql,
                       pagination_sql=pagination_sql,
                       placeholder_values=placeholder_values)

    def _resolve_cover_info(self, cover_ref: str | None):
        if cover_ref is None:
            return cover_ref
        if self.topic == ValidTopics.fiction:
            main_url = f"{self.libgen_fiction_base}/{cover_ref}"
            rocks_url = f"{self.libgenrocks_fiction_base}/{cover_ref}"
        else:
            main_url = f"{self.libgen_scitech_base}/{cover_ref}"
            rocks_url = f"{self.libgenrocks_scitech_base}/{cover_ref}"
        cover_info = CoverInfo(libgen_main=main_url, libgen_rocks=rocks_url)
        return cover_info

    def _list_as_models(self, result_set: list[dict]) -> list[SearchEntry]:
        models_list: list[SearchEntry] = []
        # Keys of elements that, if None/"", should invalidate an entry.
        # These are the MD5, title, and authors indexes, respectively.
        # The SQL query already has protection against such cases, but better safe than sorry.
        required_elements_keys = ["MD5", "Title", "Author"]

        for db_result in result_set:
            result = db_result.copy()
            invalid_element = False
            for [k, v] in result.items():
                if k in required_elements_keys:
                    if v is None or v == "":
                        invalid_element = True
                        break
                else:
                    if v is None or v == "":
                        result[k] = None

            if invalid_element:
                continue
            try:
                result_as_model = SearchEntry(
                    authors=result.get("Author"),
                    title=result.get("Title"),
                    md5=result.get("MD5"),
                    topic=self.topic,
                    language=result.get("Language"),
                    extension=result.get("Extension"),
                    size=self._bytes_to_size(result.get("Filesize")),
                    cover_info=self._resolve_cover_info(result.get("Coverurl"))
                )
                models_list.append(result_as_model)
            except ValidationError as e:
                print(e)

        return models_list

    def _build_pagination_info(self, num_of_rows: int):
        results_per_page = 25
        current_page = self.query.page
        total_pages = math.floor(int(num_of_rows / results_per_page))
        has_next_page = current_page + 1 < total_pages
        return SearchPaginationInfo(current_page=current_page,
                                    has_next_page=has_next_page,
                                    total_pages=total_pages)

    async def get_pagination_info(self) -> SearchPaginationInfo | None:
        try:
            async with MySQLConnect() as cursor:
                await cursor.execute(self.pagination_sql, args=self.placeholder_values)
                affected_rows = await cursor.fetchall()
                try:
                    num_of_rows = affected_rows[0]["COUNT(*)"]
                    pagination_info = self._build_pagination_info(num_of_rows)
                    return pagination_info
                except (IndexError, KeyError, ValidationError):
                    return None
        except Error as e:
            print("Error while connecting to database: ", e)
            return None

    async def save_on_cache(self, result: SearchResponse):
        try:
            results_stringfied = json.dumps(result.dict())
        except BaseException:
            raise ValueError("Error while stringfying results.")

        try:
            query_stringfied = json.dumps(self.query.dict())
        except BaseException:
            raise ValueError("Error while stringfying search query")

        async with RedisConnection() as redis:
            expires_in = self.expires_in(12)
            await redis.set(f"{query_stringfied}-{self.topic}-search", results_stringfied, ex=expires_in)

    async def find_search_on_cache(self) -> list[dict] | None:
        query_stringfied = json.dumps(self.query.dict())
        async with RedisConnection() as redis:
            possible_cache = await redis.get(f"{query_stringfied}-{self.topic}-search")
            if possible_cache:
                try:
                    possible_cache_obj: list[dict] = json.loads(possible_cache)
                    return possible_cache_obj
                except:
                    return None
        return None

    async def retrieve_from_cache(self) -> SearchResponse | None:
        query_stringfied = json.dumps(self.query.dict())
        try:
            async with RedisConnection() as redis:
                possible_cache = await redis.get(f"{query_stringfied}-{self.topic}-search")
                if possible_cache:
                    try:
                        cache_as_dict = json.loads(possible_cache)
                        cache_as_model = SearchResponse(**cache_as_dict)
                        return cache_as_model

                    except BaseException as e:
                        print(e)
                        return None

        except BaseException as e:
            print(e)
            return None

    async def _find_on_database(self) -> list[dict]:
        async with MySQLConnect() as cursor:
            await cursor.execute(self.search_sql, args=self.placeholder_values)
            results = await cursor.fetchall()
            return results

    async def make_search(self) -> list[SearchEntry]:
        try:
            results = await self._find_on_database()
        except Error as e:
            print("Error while connecting to database: ", e)
            raise HTTPException(500, "Couldn't connect to database.")

        if len(results) == 0:
            raise HTTPException(400, "No entry found for the given query. Please check query parameters.")
        results_as_models = self._list_as_models(results)
        print(results_as_models)
        if len(results_as_models) == 0:
            raise HTTPException(500, "Couldn't validate results.")

        return results_as_models
