from bson import ObjectId
from fastapi import HTTPException
from pydantic import ValidationError

from config.mongodb_connection import mongodb_comments_connect
from models.body_models import IdentifiedComment, Comment, Reply, IdentifiedReply
from pymongo.results import UpdateResult

class CommentsService:

    def __init__(self):
        self.db_connection = mongodb_comments_connect()
        pass

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
        index = 0

        for db_comment in entry_list:
            db_comment_model = IdentifiedComment(**db_comment)
            if db_comment_model.id == entry_id:
                return index
            index += 1

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



    def _find_reply_parent(self, comments_list: list[dict], comment_id: str) -> dict | None:
        parent_comment_index = self._find_entry_position(comments_list, comment_id)
        if isinstance(parent_comment_index, int):
            try:
                parent_comment = comments_list[parent_comment_index]
                return parent_comment
            except ValueError:
                return None
        else:
            return None

    async def _pull_comment(self, md5: str, comment_id: str):
        connection = self.db_connection
        try:
            await connection.update_one({"md5": md5}, {"$pull": {"comments": {"id": comment_id}}})
        except BaseException:
            raise HTTPException(500, "Comment couldn't be removed. This is probably an internal issue.")

    async def _push_comment(self, md5: str, comment_to_add: IdentifiedComment, position: int = None):
        connection = self.db_connection
        # Transforms ObjectID string to an actual ObjectID
        # Be mindful that embedded documents such as the documents inside an array can't have an actual "_id" field.
        # We are making a custom id field and using it as a reference because ObjectID is fast to create and unique.

        try:
            if position:
                await connection.update_one({"md5": md5},
                                            {"$addToSet": {"comments": {"$each": [comment_to_add.dict()],
                                                                        "$position": position}}})
            # Be mindful that addToSet creates an array if it doesn't exists, and then adds the specified values.
            await connection.update_one({"md5": md5}, {"$addToSet": {"comments": comment_to_add.dict()}})

        except BaseException:
            raise HTTPException(500, "Comment could not be added. This is probably an internal issue.")

    async def _pull_reply(self, md5: str, comment_id: str, reply_id: str):
        connection = self.db_connection
        try:
            # TODO: add update query description.
            await connection.update_one({"md5": md5},
                                        {"$pull": {"comments.$[elem].attached_responses": {"id": reply_id}}}
                                        ,array_filters=[{"elem.id": comment_id}])
        except BaseException:
            raise HTTPException(500, "Reply couldn't be removed. This is probably an internal issue.")

    async def _push_reply(self, md5: str, reply_to_add: IdentifiedReply, position: int = None):
        connection = self.db_connection
        try:
            if isinstance(position, int):
                await connection.update_one(
                    {"md5": md5},
                    {"$push": {"comments.$[elem].attached_responses": {"$each": [reply_to_add.dict()], "$position": position}}},
                    array_filters=[{"elem.id": reply_to_add.comment_id}], upsert=False)

            await connection.update_one(
                {"md5": md5}, {"$push": {"comments.$[elem].attached_responses": reply_to_add.dict()}},
                array_filters=[{"elem.id": reply_to_add.comment_id}], upsert=False)

        except BaseException:
            raise HTTPException(500, "Couldn't add reply. This is probably an internal issue.")

    async def get_possible_comments(self, md5: str) -> list[dict]:
        connection = self.db_connection
        # Retrieves a given md5's comments and projects the query to only return the "comments" array.
        possible_comments: dict | None = await connection.find_one({"md5": md5}, {"comments": 1, "_id": 0})
        if possible_comments is None or possible_comments.get("comments") is None:
            raise HTTPException(400, "No comments match the given MD5.")
        return possible_comments.get("comments")

    async def remove_comment(self, md5: str, comment_id: str):
        book_comments = await self.get_possible_comments(md5)
        if self._is_entry_in_list(book_comments, comment_id):
            await self._pull_comment(md5, comment_id)
        else:
            raise HTTPException(400, "No comment corresponds to the given ID.")

    async def add_comment(self, md5: str, comment: Comment):
        connection = self.db_connection
        try:
            book_comments = await self.get_possible_comments(md5)
        except HTTPException:
            book_comments = None

        identified_comment = self._identify_comment(comment)
        if isinstance(book_comments, list):
            if self._is_entry_duplicated(book_comments, comment):
                raise HTTPException(400, "Duplicated comment.")

            await self._push_comment(md5, identified_comment)

        else:
            book_comments = {
                "md5": md5,
                "comments": [identified_comment.dict()]
            }
            try:
                await connection.insert_one(book_comments)
            except BaseException:
                raise HTTPException(500, "Comment could not be added. This is probably an internal issue.")

    async def update_comment(self, md5: str, target_comment_id: str, updated_comment: Comment):
        book_comments = await self.get_possible_comments(md5)
        # Checks if target comment really exists
        if self._is_entry_in_list(book_comments, target_comment_id):
            target_comment_position = self._find_entry_position(book_comments, target_comment_id)
            await self._pull_comment(md5, target_comment_id)
            identified_comment = self._identify_comment(updated_comment)
            await self._push_comment(md5, identified_comment, target_comment_position)
        else:
            raise HTTPException(400, "Target comment doesn't exist on md5's comments' list.")

    async def remove_reply(self, md5: str, reply_to_remove: IdentifiedReply):
        book_comments = await self.get_possible_comments(md5)
        parent_comment = self._find_reply_parent(book_comments, reply_to_remove.comment_id)
        if parent_comment:
            parent_comment_replies: list[dict] = parent_comment.get("attached_responses")
            reply_index = self._find_entry_position(parent_comment_replies, reply_to_remove.id)
            if reply_index is None:
                raise HTTPException(400, "No reply found with the given id.")
            await self._pull_reply(md5, reply_to_remove.comment_id, reply_to_remove.id)
        else:
            raise HTTPException(400, "No comments match the reply's comment id.")

    async def add_reply(self, md5: str, reply_to_add: Reply):
        book_comments = await self.get_possible_comments(md5)
        parent_comment = self._find_reply_parent(book_comments, reply_to_add.comment_id)
        if parent_comment:
            parent_comment_replies: list[dict] = parent_comment.get("attached_responses")
            if self._is_entry_duplicated(parent_comment_replies, reply_to_add):
                raise HTTPException(400, "Duplicated reply.")
            identified_reply = self._identify_reply(reply_to_add)
            await self._push_reply(md5, identified_reply)

        else:
            raise HTTPException(400, "No comments match the reply's comment id.")
