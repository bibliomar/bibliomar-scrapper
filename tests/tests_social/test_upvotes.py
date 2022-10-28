from unittest import IsolatedAsyncioTestCase

from fastapi import HTTPException

from models.body_models import CommentUpvoteRequest, ReplyUpvoteRequest
from services.social.comments_service import CommentsService
from services.social.upvotes_service import UpvotesService


class TestComments(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.comments_service = CommentsService()
        self.upvotes_service = UpvotesService()
        self.test_md5 = "TEST3030303030303030303030303030"

    async def get_comments(self):
        return await self.comments_service.get_possible_comments(self.test_md5)

    async def get_test_comment_id(self):
        get = await self.get_comments()
        test_comment = get[0]
        return test_comment["id"]

    async def get_test_reply_id(self):
        get = await self.get_comments()
        parent_comment = get[0]
        reply = parent_comment["attached_responses"][0]
        return reply["id"]

    async def test_comment_upvote(self):
        _id = await self.get_test_comment_id()
        upvote_request = CommentUpvoteRequest(md5=self.test_md5, username="tester", id=_id)
        try:
            await self.upvotes_service.add_comment_upvote(upvote_request)
        except HTTPException as e:
            if e.detail.find("already") != -1:
                pass
            else:
                raise e

    async def test_remove_comment_upvote(self):
        _id = await self.get_test_comment_id()
        upvote_request = CommentUpvoteRequest(md5=self.test_md5, username="tester", id=_id)
        try:
            await self.upvotes_service.remove_comment_upvote(upvote_request)
        except HTTPException as e:
            if e.detail.find("not") != -1:
                pass
            else:
                raise e

    async def test_reply_upvote(self):
        parent_id = await self.get_test_comment_id()
        reply_id = await self.get_test_reply_id()

        upvote_request = ReplyUpvoteRequest(md5=self.test_md5, username="tester", parent_id=parent_id, id=reply_id)
        try:
            await self.upvotes_service.add_reply_upvote(upvote_request)
        except HTTPException as e:
            if e.detail.find("already") != -1:
                pass
            else:
                raise e

    async def test_remove_reply_update(self):
        parent_id = await self.get_test_comment_id()
        reply_id = await self.get_test_reply_id()

        upvote_request = ReplyUpvoteRequest(md5=self.test_md5, username="tester", parent_id=parent_id, id=reply_id)
        try:
            await self.upvotes_service.remove_reply_upvote(upvote_request)
        except HTTPException as e:
            if e.detail.find("not") != -1:
                pass
            else:
                raise e


