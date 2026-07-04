import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db.session import get_db
from app.models.user import User
from app.services.telegram_auth import TelegramAuthError, decode_access_token


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> User:
    if authorization is None:
        raise _unauthorized()

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise _unauthorized()

    try:
        payload = decode_access_token(token, secret=settings.jwt_secret)
        user_id = uuid.UUID(str(payload["sub"]))
    except (TelegramAuthError, KeyError, ValueError):
        raise _unauthorized() from None

    user = db.scalars(select(User).where(User.id == user_id)).one_or_none()
    if user is None:
        raise _unauthorized()
    return user


def _unauthorized() -> HTTPException:
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
