from fastapi import APIRouter, Depends, Response, HTTPException

from models.body_models import Comment, Reply, CommentUpdateRequest, \
    ReplyUpdateRequest
from models.query_models import CommentsQuery
from routers.user_routes import oauth2_scheme
from services.security.hashing_functions import jwt_decode
from services.social.comments_service import CommentsService

router = APIRouter(prefix="/v1")


def validate_username(payload: dict, username: str):
    sub = payload.get("sub")
    if not sub == username:
        raise HTTPException(400, "Username doesn't correspond to JWT Token.")


@router.get("/comments/{md5}", tags=["comments"])
async def get_comments(query: CommentsQuery = Depends(), handler: CommentsService = Depends()):
    comments = await handler.get_sorted_comments(query)
    return {"results": comments}


@router.post("/comments/{md5}", tags=["comments"])
async def add_new_comment(comment: Comment, handler: CommentsService = Depends(), token: str = Depends(oauth2_scheme)):
    validate_username(jwt_decode(token), comment.username)
    await handler.add_comment(comment)
    return Response(status_code=201)


@router.put("/comments/{md5}", tags=["comments"])
async def update_comment(update_request: CommentUpdateRequest, handler: CommentsService = Depends(),
                         token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.update_comment(update_request)


@router.delete("/comments/{md5}", tags=["comments"])
async def remove_comment(comment_id: str, handler: CommentsService = Depends(), token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.remove_comment(comment_id)


@router.post("/comments/{md5}/responses", tags=["comments"])
async def add_comment_response(reply: Reply, handler: CommentsService = Depends(),
                               token: str = Depends(oauth2_scheme)):
    """
    Adds a reply to a given comment
    """
    jwt_decode(token)
    await handler.add_reply(reply)
    return Response(status_code=201)


@router.put("/comments/{md5}/responses", tags=["comments"])
async def update_comment_response(update_request: ReplyUpdateRequest, handler: CommentsService = Depends(),
                                  token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.update_reply(update_request)


@router.delete("/comments/{md5}/responses", tags=["comments"])
async def remove_comment_response(comment_id: str, reply_id: str, handler: CommentsService = Depends(),
                                  token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.remove_reply(comment_id, reply_id)
