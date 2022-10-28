from fastapi import APIRouter, Depends, Query, Response

from models.body_models import md5_reg, IdentifiedComment, IdentifiedReply, Comment, Reply, CommentUpdateRequest, \
    ReplyUpdateRequest
from models.response_models import CommentResponse
from routers.v1.user_routes import oauth2_scheme
from services.security.hashing_functions import jwt_decode
from services.social.comments_service import CommentsService

router = APIRouter(prefix="/v1")


@router.get("/comments/{md5}", tags=["comments"])
async def get_comments(md5: str = Query(..., regex=md5_reg), handler: CommentsService = Depends()):
    comments = await handler.get_possible_comments(md5)
    return {"results": comments}


@router.post("/comments/{md5}", response_model=CommentResponse, tags=["comments"])
async def add_new_comment(comment: Comment, md5: str = Query(..., regex=md5_reg),
                          handler: CommentsService = Depends(), token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.add_comment(md5, comment)
    return Response(status_code=201)


@router.put("/comments/{md5}", tags=["comments"])
async def update_comment(update_request: CommentUpdateRequest, md5: str = Query(..., regex=md5_reg),
                         handler: CommentsService = Depends(), token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.update_comment(md5, update_request)


@router.delete("/comments/{md5}", tags=["comments"])
async def remove_comment(comment_id: str, md5: str = Query(..., regex=md5_reg),
                         handler: CommentsService = Depends(), token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.remove_comment(md5, comment_id)


@router.post("/comments/{md5}/responses", tags=["comments"])
async def add_comment_response(reply: Reply,
                               md5: str = Query(..., regex=md5_reg),
                               handler: CommentsService = Depends(),
                               token: str = Depends(oauth2_scheme)):
    """
    Adds a reply to a given comment
    """
    jwt_decode(token)
    await handler.add_reply(md5, reply)
    return Response(status_code=201)


@router.put("/comments/{md5}/responses", tags=["comments"])
async def update_comment_response(update_request: ReplyUpdateRequest,
                                  md5: str = Query(..., regex=md5_reg),
                                  handler: CommentsService = Depends(),
                                  token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.update_reply(md5, update_request)


@router.delete("/comments/{md5}/responses", tags=["comments"])
async def remove_comment_response(comment_id: str, reply_id: str, md5: str = Query(..., regex=md5_reg),
                                  handler: CommentsService = Depends(),
                                  token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.remove_reply(md5, comment_id, reply_id)
