from fastapi import APIRouter

from milkdown.app.api.endpoints import eventgpt, user, chat, verify

router = APIRouter()
router.include_router(eventgpt.router, prefix="/eventgpt", tags=["example_event_gpt"])
router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(verify.router, prefix="/verify", tags=["verify"])
