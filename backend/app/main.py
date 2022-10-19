from fastapi import FastAPI, Header, HTTPException, Depends
from starlette.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every  # type: ignore[import]

from app.settings import settings
from app.data_router import router

from my_feed.log import logger


def bearer_auth(token: str = Header(default="")) -> None:
    if settings.BEARER_SECRET.strip() == "":
        return
    assert len(settings.BEARER_SECRET) > 0
    if token == settings.BEARER_SECRET:
        return
    raise HTTPException(status_code=401, detail="Need to pass bearer secret to update")


def create_app() -> FastAPI:
    current_app = FastAPI(title="my_feed")

    if settings.BACKEND_CORS_ORIGINS:
        current_app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    current_app.include_router(router, prefix="/data")

    @current_app.get("/check")
    async def check(token: None = Depends(bearer_auth)) -> str:
        from app.load_pickle import update_data

        added = update_data()
        return f"OK; added {added}"

    @current_app.on_event("startup")
    async def _startup() -> None:
        from app.db import init_db

        init_db()
        await _tasks()

    @repeat_every(seconds=60 * 60 * 6, logger=logger)
    async def _tasks() -> None:
        from app.load_pickle import update_data

        update_data()

    return current_app


app = create_app()
