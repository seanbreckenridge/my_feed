from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from config import settings
from data_router import router


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

    @current_app.on_event("startup")
    def _startup() -> None:
        print("starting up!")

    return current_app


app = create_app()
