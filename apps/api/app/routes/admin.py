from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.config import Settings, get_settings


def require_admin(
    settings: Annotated[Settings, Depends(get_settings)],
    x_admin_secret: Annotated[str | None, Header()] = None,
) -> None:
    if not settings.allow_admin_endpoints:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin endpoints are disabled")
    if not x_admin_secret or x_admin_secret != settings.admin_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin secret")
