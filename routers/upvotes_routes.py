from fastapi import APIRouter, Depends, Response

from models.body_models import CommentUpvoteRequest, ReplyUpvoteRequest
from routers.user_routes import oauth2_scheme
from services.security.hashing_functions import jwt_decode
from services.social.upvotes_service import UpvotesService

router = APIRouter(prefix="/v1")


@router.post("/upvotes/{md5}", tags=["upvotes"])
async def add_comment_upvote(upvote_request: CommentUpvoteRequest,
                             handler: UpvotesService = Depends(),
                             token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.add_comment_upvote(upvote_request)
    return Response(status_code=201)


@router.delete("/upvotes/{md5}", tags=["upvotes"])
async def remove_comment_upvote(downvote_request: CommentUpvoteRequest,
                                handler: UpvotesService = Depends(),
                                token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.remove_comment_upvote(downvote_request)


@router.post("/upvotes/{md5}/responses", tags=["upvotes"])
async def add_reply_upvote(upvote_request: ReplyUpvoteRequest,
                           handler: UpvotesService = Depends(),
                           token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.add_reply_upvote(upvote_request)


@router.delete("/upvotes/{md5}/responses", tags=["upvotes"])
async def remove_reply_upvote(downvote_request: ReplyUpvoteRequest,
                              handler: UpvotesService = Depends(),
                              token: str = Depends(oauth2_scheme)):
    jwt_decode(token)
    await handler.remove_reply_upvote(downvote_request)
