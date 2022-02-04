from datetime import date, datetime
from typing import Optional, Iterator

from sqlmodel import SQLModel, Field, create_engine, Session  # type: ignore[import]

from my_feed.log import logger
from app.settings import settings


# base non-table sql model
class FeedBase(SQLModel):  # type: ignore
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
    when: datetime
    release_date: Optional[date] = Field(default=None)

    # urls
    image_url: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)


# feedbase, with an ID/table
class FeedModel(FeedBase, table=True):  # type: ignore
    id: int = Field(index=True, primary_key=True)

    # store JSON as strings, these are only used on the frontend anyways
    tags: str = Field(default=r"[]")  # List[str]
    data: Optional[bytes] = Field(default=None)  # Dict[str, Any]


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
