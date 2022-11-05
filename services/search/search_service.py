import asyncio
import json
import math
from fastapi import HTTPException, Depends, Path
from pydantic import ValidationError, BaseModel

import logging
from pymysql.err import Error
from hurry.filesize import size, alternative
from starlette.background import BackgroundTasks

from config.mysql_connection import MySQLConnect
from config.redis_connection import RedisConnection
from models.body_models import SearchEntry
from models.query_models import ValidTopics, SearchQuery, ValidCriteria
from models.response_models import SearchPaginationInfo, SearchResponse


class SQLData(BaseModel):
    search_sql: str
    pagination_sql: str
    placeholder_values: list
    pagination_placeholder_values: list


class DualSearchAwaitables(BaseModel):
    fiction_response: SearchResponse | HTTPException
    scitech_response: SearchResponse | HTTPException

    class Config:
        arbitrary_types_allowed = True


class DualSearchService:
    """
    This services implements methods that make dual search requests, return both fiction and sci-tech data.
    The main goal of this service is to serve as a short-hand for requests to both topics,
    without having to modify the original SearchService, while also making use of the Redis cache.
    """

    def __init__(self, search_params: SearchQuery = Depends()):
        self.query = search_params
        self.logger = logging.getLogger("biblioterra")

    @staticmethod
    def _awaitables_as_model(awaitables: tuple):
        return DualSearchAwaitables(fiction_response=awaitables[0], scitech_response=awaitables[1])

    def _raise_terminating_exception(self, awaitables: tuple[HTTPException, HTTPException]):
        """
        Raises the biggest priority exception. 500 codes take priority over 400 ones.
        """
        fiction_exc = awaitables[0]
        scitech_exc = awaitables[1]

        if fiction_exc.status_code == 500:
            tobe_raised = fiction_exc
            raise tobe_raised
        elif scitech_exc.status_code == 500:
            tobe_raised = scitech_exc
            raise scitech_exc
        else:
            tobe_raised = fiction_exc

        self.logger.error(tobe_raised)
        raise tobe_raised

    def _score_as_key(self, item: SearchEntry):
        try:
            score = item.relevance
            if score is not None:
                return score
        except (KeyError, IndexError) as e:
            self.logger.warning("Using score ordering in object without score property.", exc_info=e)

    def _sort_by_relevance(self, results_list: list):
        results_list.sort(key=self._score_as_key, reverse=True)

    def _handle_dual_pagination(self, awaitables: DualSearchAwaitables) -> SearchPaginationInfo | None:
        valid_total_pages = []
        for item in (awaitables.fiction_response, awaitables.scitech_response):
            if not isinstance(item, HTTPException):
                pagination = item.pagination
                if pagination is not None:
                    valid_total_pages.append(pagination.total_pages)

        if not bool(valid_total_pages):
            return None

        else:
            max_possible_page = max(valid_total_pages)

        current_page = self.query.page
        total_pages = max_possible_page
        has_next_page = current_page + 1 < total_pages
        return SearchPaginationInfo(current_page=current_page,
                                    has_next_page=has_next_page,
                                    total_pages=total_pages)

    @staticmethod
    def _handle_dual_results(awaitables: DualSearchAwaitables) -> list[SearchEntry]:
        valid_results: list[SearchEntry] = []
        for item in (awaitables.fiction_response, awaitables.scitech_response):
            if not isinstance(item, HTTPException):
                entries_list: list[SearchEntry] = item.results

                # Equivalent to "is not None and len() > 0"
                if not isinstance(entries_list, HTTPException) and bool(entries_list):
                    valid_results.extend(entries_list)

        if not bool(valid_results):
            raise HTTPException(400, "No results found for the given query (on both topics). Please check"
                                     "query parameters.")

        return valid_results

    async def search_handler(self, topic: ValidTopics) -> SearchResponse | HTTPException:
        search_service = SearchService(self.query, topic)

        possible_cache = await search_service.retrieve_from_cache()
        if possible_cache:
            return possible_cache

        search_awaitables = await asyncio.gather(
            search_service.make_search(), search_service.get_pagination_info(),
            return_exceptions=True
        )

        search_results: list[SearchEntry] | HTTPException = search_awaitables[0]
        search_pagination: SearchPaginationInfo | None = search_awaitables[1]
        if not isinstance(search_results, HTTPException):
            if isinstance(search_pagination, BaseException):
                search_pagination = None
            search_response = SearchResponse(pagination=search_pagination, results=search_results)
            await search_service.save_on_cache(search_response)
            return search_response
        else:
            return search_results

    async def make_dual_search(self):
        # To avoid wasting too much time, we need to use asyncio.gather() (or TaskGroups in the future)
        # to concurrently call all async methods.
        awaitables = await asyncio.gather(
            self.search_handler(ValidTopics.fiction), self.search_handler(ValidTopics.scitech)
            , return_exceptions=True)
        if isinstance(awaitables[0], HTTPException) and isinstance(awaitables[1], HTTPException):
            self._raise_terminating_exception(awaitables)

        awaitables_as_model = self._awaitables_as_model(awaitables)
        results = self._handle_dual_results(awaitables_as_model)
        self._sort_by_relevance(results)
        pagination = self._handle_dual_pagination(awaitables_as_model)
        response = SearchResponse(pagination=pagination, results=results)
        return response



class SearchService:
    """
    This is the improved search service that makes queries directly to a mysql database.
    """

    def __init__(self, search_params: SearchQuery = Depends(), topic: ValidTopics = Path(...)):
        self.topic = topic
        self.query = search_params
        self.logger = logging.getLogger("biblioterra")
        self.results_per_page = self.query.results_per_page

        sql_handler = self._sql_query_builder()

        self.search_sql = sql_handler.search_sql
        self.pagination_sql = sql_handler.pagination_sql
        self.placeholder_values = sql_handler.placeholder_values
        self.pagination_placeholder_values = sql_handler.pagination_placeholder_values

    @staticmethod
    def bytes_to_size(size_to_convert: int | str):
        if size_to_convert is None or int(size_to_convert) == 0:
            return "0 B"
        return size(int(size_to_convert), system=alternative)

    @staticmethod
    def expires_in(hours: int):

        if hours is None:
            hours = 4
        # 3600 seconds is equivalent to 1 hour.
        return hours * 3600

    @staticmethod
    def resolve_cover_url(topic: ValidTopics, cover_ref: str | None):
        libgen_fiction_base = "https://libgen.is/fictioncovers"
        libgen_scitech_base = "https://libgen.is/covers"

        if cover_ref is None:
            return cover_ref

        if topic == ValidTopics.fiction:
            cover_url = f"{libgen_fiction_base}/{cover_ref}"

        else:
            cover_url = f"{libgen_scitech_base}/{cover_ref}"

        return cover_url

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

        relevance_sql = f"MATCH( {sql_criteria} ) AGAINST(%s) as score"

        search_sql = f"""
        SELECT MD5, Title, Author, Language, Extension, Filesize, Coverurl, {relevance_sql} from {table} 
        WHERE MATCH( {sql_criteria} ) AGAINST(%s) AND MD5 != '' AND Title != '' AND Author != ''
        """

        pagination_sql = f"""
        SELECT COUNT(*) from {table} 
        WHERE MATCH( {sql_criteria} ) AGAINST(%s) AND MD5 != '' AND Title != '' AND Author != ''
        """

        # Because we have two starting "%s" (placeholder values), we start the array with the query repeated
        # two times. There's probably a better way to do this. But we also need to escape these values, so no
        # direct string injection.
        placeholder_values = [self.query.q, self.query.q]
        pagination_placeholder_values = [self.query.q]

        lang = self.query.language
        _format = self.query.format

        if lang:
            lang_sql = """AND Language = %s"""
            search_sql += lang_sql
            pagination_sql += lang_sql

            placeholder_values.append(lang)
            pagination_placeholder_values.append(lang)

        if _format:
            _format_sql = """AND Extension = %s"""
            search_sql += _format_sql
            pagination_sql += _format_sql

            placeholder_values.append(_format)
            pagination_placeholder_values.append(_format)

        if self.query.page == 1:
            offset = 0
        else:
            offset = (self.query.page - 1) * self.results_per_page
        limit_end = offset + self.results_per_page

        # Only adds LIMIT to search sql
        search_sql += f"""LIMIT {offset},{limit_end}"""

        return SQLData(search_sql=search_sql,
                       pagination_sql=pagination_sql,
                       placeholder_values=placeholder_values,
                       pagination_placeholder_values=pagination_placeholder_values)

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
                    size=self.bytes_to_size(result.get("Filesize")),
                    cover_url=self.resolve_cover_url(self.topic, result.get("Coverurl")),
                    relevance=result.get("score")
                )

                models_list.append(result_as_model)

            except ValidationError as e:
                self.logger.error(e)

        return models_list

    def _build_pagination_info(self, num_of_rows: int):
        current_page = self.query.page
        if num_of_rows >= self.results_per_page:
            total_pages = math.floor(num_of_rows / self.results_per_page)
        else:
            total_pages = 1
        has_next_page = current_page + 1 < total_pages
        return SearchPaginationInfo(current_page=current_page,
                                    has_next_page=has_next_page,
                                    total_pages=total_pages)

    async def get_pagination_info(self) -> SearchPaginationInfo | None:
        try:
            async with MySQLConnect() as cursor:
                await cursor.execute(self.pagination_sql, args=self.pagination_placeholder_values)
                affected_rows = await cursor.fetchall()
                try:
                    num_of_rows = affected_rows[0]["COUNT(*)"]
                    if num_of_rows == 0:
                        return None
                    pagination_info = self._build_pagination_info(num_of_rows)
                    return pagination_info
                except (IndexError, KeyError, ValidationError) as e:
                    self.logger.warning(e)
                    return None
        except Error as e:
            self.logger.error(e)
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
                        self.logger.info(e)
                        return None

        except BaseException as e:
            self.logger.error(e)
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
            self.logger.error(e)
            raise HTTPException(500, "Couldn't connect to database.")

        # Equivalent to "is None or len() == 0".
        if not bool(results):
            raise HTTPException(400, "No entry found for the given query. Please check query parameters.")

        results_as_models = self._list_as_models(results)

        # Equivalent to "is None or len() == 0".
        if not bool(results_as_models):
            if len(results) != 0:
                self.logger.warning(f"The result list: {results}")
                self.logger.warning("Failed to return any results as models.")
                self.logger.warning("This may be a schema issue.")
            raise HTTPException(500, "No valid result returned.")

        return results_as_models
