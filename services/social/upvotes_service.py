from fastapi import HTTPException, Depends
from pydantic import ValidationError

from config.mongodb_connection import mongodb_comments_connect
from models.body_models import IdentifiedComment, CommentUpvoteRequest, ReplyUpvoteRequest, IdentifiedReply
from services.social.comments_service import CommentsService


class UpvotesService:
    def __init__(self):
        self.db_connection = mongodb_comments_connect()
        self.comments_service = CommentsService()

    @staticmethod
    def _user_has_upvoted(upvotes_list: list[str], username: str) -> bool:
        try:
            upvotes_list.index(username)
            return True
        except ValueError:
            return False

    async def _get_comment_upvotes(self, request: CommentUpvoteRequest) -> list[str]:
        possible_comments = await self.comments_service.get_possible_comments(request.md5)
        comment_info = self.comments_service.find_entry_in_list(possible_comments, request.id)
        if comment_info:
            comment_instance = comment_info[0]
            comment = IdentifiedComment(**comment_instance)
            return comment.upvotes

        else:
            raise HTTPException(400, "Comment doesn't exist on this specific MD5.")

    async def _get_reply_upvotes(self, request: ReplyUpvoteRequest) -> list[str]:
        possible_comments = await self.comments_service.get_possible_comments(request.md5)
        parent_info = self.comments_service.find_entry_in_list(possible_comments, request.parent_id)
        if parent_info is not None:
            parent_instance = IdentifiedComment(**parent_info[0])
            parent_replies = parent_instance.attached_responses
            reply_instance = self.comments_service.find_entry_in_list(parent_replies, request.id)
            if reply_instance is None:
                raise HTTPException(400, "Couldn't find a reply with this specific ID in the comment's responses.")
            reply_model = IdentifiedReply(**reply_instance[0])
            return reply_model.upvotes

        else:
            raise HTTPException(400, "Parent comment ID doesn't match any comment in this MD5.")

    async def add_comment_upvote(self, request: CommentUpvoteRequest):
        connection = self.db_connection
        upvotes = await self._get_comment_upvotes(request)
        if self._user_has_upvoted(upvotes, request.username):
            raise HTTPException(400, "User has already upvoted this comment.")
        try:
            await connection.update_one(
                {"md5": request.md5}, {"$push": {"comments.$[elem].upvotes": request.username}},
                array_filters=[{"elem.id": request.id}], upsert=False)
        except BaseException as e:
            raise e

    async def remove_comment_upvote(self, request: CommentUpvoteRequest):
        connection = self.db_connection
        upvotes = await self._get_comment_upvotes(request)
        if not self._user_has_upvoted(upvotes, request.username):
            raise HTTPException(400, "User has not upvoted this comment.")

        try:
            await connection.update_one(
                {"md5": request.md5}, {"$pull": {"comments.$[elem].upvotes": request.username}},
                array_filters=[{"elem.id": request.id}], upsert=False)
        except BaseException as e:
            raise e

    async def add_reply_upvote(self, request: ReplyUpvoteRequest):
        connection = self.db_connection
        upvotes = await self._get_reply_upvotes(request)
        if self._user_has_upvoted(upvotes, request.username):
            raise HTTPException(400, "User has already upvoted this reply.")
        try:
            await connection.update_one(
                {"md5": request.md5},
                {"$push": {"comments.$[comment].attached_responses.$[reply].upvotes": request.username}},
                array_filters=[{"comment.id": request.parent_id}, {"reply.id": request.id}], upsert=False)

        except BaseException as e:
            raise e

    async def remove_reply_upvote(self, request: ReplyUpvoteRequest):
        connection = self.db_connection
        upvotes = await self._get_reply_upvotes(request)
        if not self._user_has_upvoted(upvotes, request.username):
            raise HTTPException(400, "User has not upvoted this reply.")

        try:
            await connection.update_one(
                {"md5": request.md5},
                {"$pull": {"comments.$[comment].attached_responses.$[reply].upvotes": request.username}},
                array_filters=[{"comment.id": request.parent_id}, {"reply.id": request.id}], upsert=False)

        except BaseException as e:
            raise e
