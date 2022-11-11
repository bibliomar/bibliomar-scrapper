from typing import Iterable

import logging
from bson import ObjectId
from fastapi import HTTPException, Query
from pydantic import ValidationError

from config.mongodb_connection import mongodb_comments_connect
from models.body_models import IdentifiedComment, Comment, Reply, IdentifiedReply, ReplyUpdateRequest, \
    CommentUpdateRequest, date_format, md5_reg
from datetime import datetime

from models.query_models import CommentsQuery, CommentSort, SortMode


class CommentSortingService:
    """
    Internal class used to provide methods for sorting comments and replies.
    """

    @staticmethod
    def _str_to_datetime(created_at: str | None):
        # Meant to be used as a map(), sort() or similar function.
        # Entries with no date are given a temporary one, this makes them appear last in the sorting.
        temp_date = datetime.strptime("2000-01-01T00:00:00Z", date_format)
        try:
            if created_at is None:
                created_at = temp_date
            elif isinstance(created_at, str):
                created_at = datetime.strptime(created_at, date_format)
        except BaseException as e:
            pass
        return created_at

    def _datetime_as_key(self, item: dict):
        return self._str_to_datetime(item["created_at"])

    @staticmethod
    def _upvotes_as_key(item: dict):
        return len(item["upvotes"])

    @staticmethod
    def _rating_as_key(item: dict):
        return item["rating"]

    @staticmethod
    def _select_sort_mode(sort_mode: SortMode):

        if sort_mode is None or sort_mode == SortMode.desc:
            return True
        else:
            return False

    def sort_comments(self, comments: list[dict], query: CommentsQuery):
        sort_mode = self._select_sort_mode(query.mode)

        if query.sort is None or query.sort == CommentSort.date:
            comments.sort(key=self._datetime_as_key, reverse=sort_mode)
        if query.sort == CommentSort.upvotes:
            comments.sort(key=self._upvotes_as_key, reverse=sort_mode)
        elif query.sort == CommentSort.rating:
            comments.sort(key=self._rating_as_key, reverse=sort_mode)

    def sort_replies(self, comments: list[dict], query: CommentsQuery):
        sort_mode = self._select_sort_mode(query.mode)
        for comment in comments:
            comment_replies: list[dict] = comment.get("attached_responses")

            # If comment_replies is None or has len() == 0.
            if not bool(comment_replies):
                continue

            # Replies can't be sortered by rating, since they don't have this attribute.
            if query.sort is None or query.sort == CommentSort.date:
                comment_replies.sort(key=self._datetime_as_key, reverse=sort_mode)

            elif query.sort == CommentSort.upvotes:
                comment_replies.sort(key=self._upvotes_as_key, reverse=sort_mode)


class CommentsService:

    def __init__(self, md5: str = Query(..., regex=md5_reg)):
        self.db_connection = mongodb_comments_connect()
        self.md5 = md5
        self.logger = logging.getLogger("biblioterra")
        self.sorting_service = CommentSortingService()

    @staticmethod
    def _append_dates(entry: IdentifiedComment | IdentifiedReply):
        # This method is extremely important. All comments/replies should have proper dates attached for the
        # sorting by date algorithm to work.

        # Appends modified_at
        if entry.modified_at is None and entry.created_at is not None:
            if isinstance(entry.modified_at, datetime):
                pass
            else:
                entry.modified_at = datetime.utcnow().strftime(date_format)

        # Appends created_at
        if entry.created_at is None:
            if isinstance(entry.modified_at, datetime):
                pass
            else:
                entry.created_at = datetime.utcnow().strftime(date_format)

    @staticmethod
    def _identify_comment(comment: Comment):
        # Identify refers to the process of adding an ID and relevant metadata to a plain comment,
        # readying it to be added to the database.
        identified_comment_id = str(ObjectId())
        try:
            identified_comment = IdentifiedComment(**comment.dict(), id=identified_comment_id)
        except ValidationError:
            raise HTTPException(500, "Couldn't identify comment.")

        return identified_comment

    @staticmethod
    def _identify_reply(reply: Reply):
        # Identify refers to the process of adding an ID and relevant metadata to a plain reply,
        # readying it to be added to the database.
        identified_reply_id = str(ObjectId())
        try:
            identified_comment = IdentifiedReply(**reply.dict(), id=identified_reply_id)
        except ValidationError:
            raise HTTPException(500, "Couldn't identify comment.")

        return identified_comment

    @staticmethod
    def _is_entry_in_list(entry_list: list[dict], entry_id: str):
        """
        This method determines if the checked comment_id exists in the entry_list (which should be a list of values
        from the database).
        If it does, then it means that it can be updated, or removed.
        """

        for db_comment in entry_list:
            db_comment_model = IdentifiedComment(**db_comment)
            if db_comment_model.id == entry_id:
                return True

        return False

    @staticmethod
    def _find_entry_position(entry_list: list[dict], entry_id: str) -> int | None:

        # TODO: convert to enumerate
        for index, db_comment in enumerate(entry_list):
            if db_comment.get("id") == entry_id:
                return index

        return None

    @staticmethod
    def _is_entry_duplicated(entry_list: list[dict], checked_entry: Comment | Reply):
        """
        This compares the checked_entry with all the values in entry_list. This method doesn't compare IDs or properties
        only available on Identified versions of the Comment and Reply schemas, so it's used to determine
        if a entry's content that is about to be added is the same as one that already exists.
        (Avoiding spam and duplicates.)
        Only use this when adding new entries.
        """
        checked_entry_dict = checked_entry.dict()

        if len(entry_list) == 0:
            return False

        for list_value in entry_list:
            is_duplicated = True
            for key, value in list_value.items():
                # Only compare values relevant to both Comment or Reply schemas.
                if key not in ["username", "content", "rating", "comment_id"]:
                    continue

                # Trying to get the current key of the value in entry list from the checked entry dict.
                # We call the variable "key" but it's actually it's value that's returned.
                # .get doesn't raise an exception, it returns a None value instead.
                checked_dict_key = checked_entry_dict.get(key)
                if checked_dict_key is None:
                    # If a key exists in list_value but not on checked_entry, it's safe to assume they are not the same.
                    is_duplicated = False
                    break

                # Comparing if the value from the checked entry dict is
                # the same as the one in the current list_value iteration.
                # If the values don't correspond, that means they are not the equal objects.
                if checked_dict_key != value:
                    is_duplicated = False
                    break

            # If at the end of a iteration, a value is deemed to be duplicated.
            if is_duplicated:
                return is_duplicated

        return False

    def find_entry_in_list(self, entry_list: list[dict], entry_id: str) -> tuple[dict, int] | None:
        # This function returns the actual comment or reply from a given list, and it's position.
        entry_position = self._find_entry_position(entry_list, entry_id)
        if isinstance(entry_position, int):
            try:
                entry_instance = entry_list[entry_position]
                return entry_instance, entry_position
            except ValueError:
                return None
        else:
            return None

    async def _pull_comment(self, comment_id: str):
        connection = self.db_connection
        try:
            await connection.update_one({"md5": self.md5}, {"$pull": {"comments": {"id": comment_id}}})
        except BaseException:
            raise HTTPException(500, "Comment couldn't be removed. This is probably an internal issue.")

    async def _push_comment(self, comment_to_add: IdentifiedComment, position: int = None):
        connection = self.db_connection
        self._append_dates(comment_to_add)

        try:

            if position:
                await connection.update_one({"md5": self.md5},
                                            {"$addToSet": {"comments": {"$each": [comment_to_add.dict()],
                                                                        "$position": position}}})
            else:
                # Be mindful that addToSet creates an array if it doesn't exists, and then adds the specified values.
                await connection.update_one({"md5": self.md5}, {"$addToSet": {"comments": comment_to_add.dict()}})

        except BaseException:
            raise HTTPException(500, "Comment could not be added. This is probably an internal issue.")

    async def _pull_reply(self, comment_id: str, reply_id: str):
        connection = self.db_connection
        try:
            # TODO: add update query description.
            await connection.update_one({"md5": self.md5},
                                        {"$pull": {"comments.$[elem].attached_responses": {"id": reply_id}}},
                                        array_filters=[{"elem.id": comment_id}])
        except BaseException:
            raise HTTPException(500, "Reply couldn't be removed. This is probably an internal issue.")

    async def _push_reply(self, reply_to_add: IdentifiedReply, position: int = None):
        connection = self.db_connection
        self._append_dates(reply_to_add)
        try:
            if isinstance(position, int):
                await connection.update_one(
                    {"md5": self.md5},
                    {"$push": {"comments.$[elem].attached_responses": {"$each": [reply_to_add.dict()],
                                                                       "$position": position}}},
                    array_filters=[{"elem.id": reply_to_add.parent_id}], upsert=False)
                return

            await connection.update_one(
                {"md5": self.md5}, {"$push": {"comments.$[elem].attached_responses": reply_to_add.dict()}},
                array_filters=[{"elem.id": reply_to_add.parent_id}], upsert=False)

        except BaseException:
            raise HTTPException(500, "Couldn't add reply. This is probably an internal issue.")

    async def get_possible_comments(self) -> list[dict]:
        connection = self.db_connection

        # Retrieves a given md5's comments and projects the query to only return the "comments" array.
        possible_comments: dict | None = await connection.find_one({"md5": self.md5}, {"comments": 1, "_id": 0})

        if possible_comments is None or not bool(possible_comments.get("comments")):
            raise HTTPException(400, "No comments match the given MD5.")
        comments_list = possible_comments.get("comments")
        return comments_list

    async def get_sorted_comments(self, query: CommentsQuery):
        comments = await self.get_possible_comments()
        self.sorting_service.sort_replies(comments, query)
        self.sorting_service.sort_comments(comments, query)

        return comments

    async def remove_comment(self, comment_id: str):
        book_comments = await self.get_possible_comments()
        if self._is_entry_in_list(book_comments, comment_id):
            await self._pull_comment(comment_id)
        else:
            raise HTTPException(400, "No comment corresponds to the given ID.")

    async def add_comment(self, comment: Comment):
        connection = self.db_connection
        try:
            book_comments = await self.get_possible_comments()
        except HTTPException:
            book_comments = None

        identified_comment = self._identify_comment(comment)
        if isinstance(book_comments, list):
            if self._is_entry_duplicated(book_comments, comment):
                raise HTTPException(400, "Duplicated comment.")

            await self._push_comment(identified_comment)

        else:
            self._append_dates(identified_comment)
            book_comments = {
                "md5": self.md5,
                "comments": [identified_comment.dict()]
            }
            try:
                if identified_comment.created_at is None:
                    e = AttributeError("Comment has no created_at attribute.")
                    self.logger.error(e)
                    raise e

                await connection.insert_one(book_comments)
            except BaseException:
                raise HTTPException(500, "Comment could not be added. This is probably an internal issue.")

    async def update_comment(self, update_request: CommentUpdateRequest):
        if update_request.updated_content is None and update_request.updated_rating is None:
            raise HTTPException(400, "Updating is not possible. No changes being made.")
        book_comments = await self.get_possible_comments()
        # Checks if target comment really exists
        entry_in_list = self.find_entry_in_list(book_comments, update_request.id)
        if entry_in_list:
            target_comment_instance = entry_in_list[0]
            target_comment_position = entry_in_list[1]
            updated_comment = IdentifiedComment(**target_comment_instance)
            if update_request.updated_content is not None:
                updated_comment.content = update_request.updated_content
            if update_request.updated_rating is not None:
                updated_comment.rating = update_request.updated_rating

            await self._pull_comment(updated_comment.id)
            await self._push_comment(updated_comment, target_comment_position)


        else:
            raise HTTPException(400, "Target comment doesn't exist on md5's comments' list.")

    async def remove_reply(self, parent_id: str, reply_id: str):
        book_comments = await self.get_possible_comments()
        parent_comment_info = self.find_entry_in_list(book_comments, parent_id)
        if self._is_entry_in_list(book_comments, parent_id) and parent_comment_info is not None:
            parent_comment = parent_comment_info[0]
            parent_comment_replies: list[dict] = parent_comment.get("attached_responses")
            reply_position = self._find_entry_position(parent_comment_replies, reply_id)
            if reply_position is None:
                raise HTTPException(400, "No reply found with the given id.")
            await self._pull_reply(parent_id, reply_id)
        else:
            raise HTTPException(400, "No comments match the reply's comment id.")

    async def add_reply(self, reply_to_add: Reply):
        book_comments = await self.get_possible_comments()
        parent_comment_info = self.find_entry_in_list(book_comments, reply_to_add.parent_id)
        if parent_comment_info is not None:
            parent_comment = parent_comment_info[0]
            parent_comment_replies: list[dict] = parent_comment.get("attached_responses")
            if self._is_entry_duplicated(parent_comment_replies, reply_to_add):
                raise HTTPException(400, "Duplicated reply.")
            identified_reply = self._identify_reply(reply_to_add)
            await self._push_reply(identified_reply)

        else:
            raise HTTPException(400, "No comments match the reply's comment id.")

    async def update_reply(self, reply_update: ReplyUpdateRequest):
        book_comments = await self.get_possible_comments()
        parent_comment_info = self.find_entry_in_list(book_comments, reply_update.parent_id)
        if parent_comment_info is not None:
            parent_comment = parent_comment_info[0]
            parent_comment_replies: list[dict] = parent_comment.get("attached_responses")
            target_reply_info = self.find_entry_in_list(parent_comment_replies, reply_update.id)
            if target_reply_info is None:
                raise HTTPException(400, "No response found for the given target id.")
            target_reply_instance = target_reply_info[0]
            target_reply_position = target_reply_info[1]
            updated_reply = IdentifiedReply(**target_reply_instance)
            updated_reply.content = reply_update.updated_content

            await self._pull_reply(updated_reply.parent_id, updated_reply.id)
            await self._push_reply(updated_reply, target_reply_position)

        else:
            raise HTTPException(400, "No comments match the given target id.")
