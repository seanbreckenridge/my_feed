from fastapi import FastAPI, Depends
from starlette.middleware.cors import CORSMiddleware

from app.settings import settings
from app.data_router import router
from app.token import bearer_auth

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
        from app.load_pickle import update_data

        init_db()
        update_data()

    return current_app


app = create_app()
