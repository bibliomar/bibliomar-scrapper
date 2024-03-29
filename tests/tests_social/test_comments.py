from unittest import IsolatedAsyncioTestCase

from fastapi import HTTPException

from models.body_models import Comment, Reply, IdentifiedReply, IdentifiedComment, CommentUpdateRequest, \
    ReplyUpdateRequest
from services.social.comments_service import CommentsService


class TestComments(IsolatedAsyncioTestCase):
    def setUp(self) -> None:

        self.test_md5 = "TEST3030303030303030303030303030"
        self.service = CommentsService(self.test_md5)

    async def get_comments(self):
        return await self.service.get_possible_comments()

    async def test_get_comments(self):
        get = await self.get_comments()
        assert len(get) >= 0


    async def test_add_comment(self):
        test_comment_content = {
            "username": "tester",
            "rating": 5,
            "content": "teste"
        }
        test_comment = Comment(**test_comment_content)
        try:

            await self.service.add_comment(test_comment)
        except HTTPException as e:
            detail = e.detail.lower()
            if detail.find("duplicated") != -1:
                pass
            else:
                raise e

    async def test_update_comment(self):
        get = await self.get_comments()
        old_comment_content = get[0]
        old_comment = IdentifiedComment(**old_comment_content)
        update_request = CommentUpdateRequest(id=old_comment.id,
                                              updated_content="this comment has been updated with $set")

        await self.service.update_comment(update_request)

    async def test_add_reply(self):
        get = await self.get_comments()

        converted_comment_id = str(get[0].get("id"))

        test_reply_content = {
            "username": "tester",
            "content": "teste de replica",
            "parent_id": converted_comment_id
        }
        test_reply = Reply(**test_reply_content)
        try:
            await self.service.add_reply(test_reply)
        except HTTPException as e:
            detail = e.detail.lower()
            if detail.find("duplicated") != -1:
                pass
            else:
                raise e

    async def test_update_reply(self):
        get = await self.get_comments()
        test_comment = get[0]
        comments_replies = test_comment.get("attached_responses")
        test_reply_content = comments_replies[0]
        test_reply_id = test_reply_content["id"]

        test_reply = Reply(**test_reply_content)
        updated_content = "conteudo modificado."
        update_request = ReplyUpdateRequest(id=test_reply_id,
                                            parent_id=test_reply.parent_id, updated_content=updated_content)
        await self.service.update_reply(update_request)

    async def test_remove_reply(self):
        get = await self.get_comments()

        parent_comment = get[0]
        parent_comment_responses = parent_comment.get("attached_responses")
        identified_reply = IdentifiedReply(**parent_comment_responses[0])
        print(identified_reply.parent_id)
        if identified_reply.username != "tester":
            return ValueError("Last comment is not from the tester user.")

        await self.service.remove_reply(identified_reply.parent_id, identified_reply.id)

    async def test_remove_comment(self):
        get = await self.get_comments()
        last_comment = get[0]
        if last_comment.get("username") != "tester":
            return ValueError("Last comment is not from the tester user.")

        await self.service.remove_comment(last_comment["id"])
        get2 = await self.service.get_possible_comments()
        self.assertNotIn(last_comment, get2)
