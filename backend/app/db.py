from datetime import date
from typing import Optional, Iterator, Dict, List, Any

from sqlmodel import SQLModel, Field, Column, create_engine, Session, JSON # type: ignore[import]

from my_feed.log import logger
from app.settings import settings


# base non-table sql model
class FeedBase(SQLModel):
    model_id: str
    ftype: str  # feed item type
    title: str
    score: Optional[float] = Field(default=None)

    # more metadata
    subtitle: Optional[str] = Field(default=None)
    creator: Optional[str] = Field(default=None)
    part: Optional[int] = Field(default=None)
    subpart: Optional[int] = Field(default=None)
    collection: Optional[str] = Field(default=None)

    # dates
    when: int
    release_date: Optional[date] = Field(default=None)

    # urls
    image_url: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)


# feedbase, with an ID/table
class FeedModel(FeedBase, table=True):
    id: int = Field(index=True, primary_key=True)

    data: str = Field(default=None)
    flags: str = Field(default=None)


feed_engine = create_engine(
    settings.SQLITE_DB_PATH,
    echo=settings.SQL_ECHO,
)


def init_db() -> None:
    logger.info("Creating tables...")
    SQLModel.metadata.create_all(feed_engine)


def get_db() -> Iterator[Session]:
    with Session(feed_engine) as session:
        yield session
