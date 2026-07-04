import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.session import get_db
from app.models.user import User
from app.services.telegram_auth import TelegramAuthError, create_access_token, validate_telegram_init_data

router = APIRouter(prefix="/auth", tags=["auth"])


class TelegramAuthRequest(BaseModel):
    init_data: str


class AuthUserRead(BaseModel):
    id: uuid.UUID
    telegram_id: int
    username: str | None = None
    first_name: str | None = None

    model_config = {"from_attributes": True}


class TelegramAuthResponse(BaseModel):
    access_token: str
    user: AuthUserRead


@router.post("/telegram", response_model=TelegramAuthResponse)
def auth_telegram(
    payload: TelegramAuthRequest,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TelegramAuthResponse:
    try:
        telegram_user = validate_telegram_init_data(
            payload.init_data,
            bot_token=settings.telegram_bot_token,
            allowed_user_ids=settings.telegram_allowed_user_ids,
        )
    except (TelegramAuthError, ValueError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram authentication"
        ) from None

    user = db.scalars(select(User).where(User.telegram_id == telegram_user.telegram_id)).one_or_none()
    if user is None:
        user = User(
            telegram_id=telegram_user.telegram_id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
        )
        db.add(user)
    else:
        user.username = telegram_user.username
        user.first_name = telegram_user.first_name

    db.commit()
    db.refresh(user)
    access_token = create_access_token(
        {"sub": str(user.id), "telegram_id": user.telegram_id},
        secret=settings.jwt_secret,
    )
    return TelegramAuthResponse(access_token=access_token, user=AuthUserRead.model_validate(user))
