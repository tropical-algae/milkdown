import json
from datetime import datetime, timedelta
from typing import Any

import pytz
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from milkdown.app.api.deps import get_current_user, get_db
from milkdown.app.core import security
from milkdown.app.core.constant import CONSTANT
from milkdown.app.db import crud

# from milkdown.app.db.crud.select import select_all_user
from milkdown.app.api.deps import topic_selector
from milkdown.app.db.models import User
from milkdown.app.models.model_chat import ChatHistory, ChatMessages, HobbyCollectRequest, PlayerStatus
from milkdown.app.models.model_user import Token, UserBase
from milkdown.common.config import settings


router = APIRouter()


@router.post("/about_hobbies")
async def chat_about_hobbies(
    data: HobbyCollectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pass


@router.post("/random_topic")
async def chat_random_topic(
    player_status: PlayerStatus
    # current_user: User = Depends(get_current_user)
) -> ChatMessages:
    genr, _ = topic_selector.random_topic(player_status=player_status)

    if genr:
        messages: ChatMessages = await genr.initiate_conversation(player_status=player_status)
    else:
        raise HTTPException(status_code=500, detail=CONSTANT.TOPIC_SELECT_ERROR)

    return messages

@router.post("/continue_topic")
async def chat_continue_topic(
    history: ChatHistory,
    player_status: PlayerStatus
    # current_user: User = Depends(get_current_user)
) -> ChatHistory:
    topic_type = history.topic_type
    genr = topic_selector.continue_topic(topic_type=topic_type)
    
    if genr:
        messages: ChatHistory = await genr.continue_conversation(player_status=player_status, history=history)
    else:
        raise HTTPException(status_code=500, detail=CONSTANT.TOPIC_TYPE_VERIFY_ERROR)

    return messages
