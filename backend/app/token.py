from fastapi import Header, HTTPException

from app.settings import settings


def bearer_auth(token: str = Header(default="")) -> None:
    if settings.BEARER_SECRET.strip() == "":
        return
    assert len(settings.BEARER_SECRET) > 0
    if token == settings.BEARER_SECRET:
        return
    raise HTTPException(status_code=401, detail="Need to pass bearer secret to update")
