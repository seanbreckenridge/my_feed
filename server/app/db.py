from datetime import date, datetime
from typing import Optional, Generator

from sqlmodel import SQLModel, Field, create_engine, Session

from my_feed.sources.model import FeedItem, DateIsh
from app.settings import settings


class FeedModel(SQLModel, table=True):  # type: ignore
    # basics
    id: int = Field(index=True, primary_key=True)
    model_id: str = Field(index=True)
    ftype: str  # feed item type
    title: str
    score: Optional[float] = Field(default=None)

    # more metadata
    subtitle: Optional[str] = Field(default=None)
    creator: Optional[str] = Field(default=None)
    part: Optional[int] = Field(default=None)
    subpart: Optional[int] = Field(default=None)
    collection: Optional[str] = Field(default=None)
    # tags: Tags = field(default_factory=list)  # extra information/tags for this item
    # data: Dict[str, Any] = field(default_factory=dict)

    # dates
    # split the when union on the dataclass across fields
    # fix stuff when querying up so I don't lose any accuracy
    when_dt: Optional[datetime] = Field(default=None)
    when_date: Optional[date] = Field(default=None)
    when_year: Optional[int] = Field(default=None)
    release_date: Optional[date] = Field(default=None)

    # urls
    image_url: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)


engine = create_engine(
    settings.SQLITE_DB_PATH,
    echo=True,
)


def init_db():
    FeedModel.__table__.create(bind=engine)
    #SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    # TODO: add check for new pickle files and load any new data
    with Session(engine) as session:
        yield session
