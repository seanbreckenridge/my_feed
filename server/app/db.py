import json
import pickle
from pathlib import Path
from datetime import date, datetime
from typing import Optional, Generator, Iterator

from sqlmodel import SQLModel, Field, create_engine, Session, select  # type: ignore[import]

from my_feed.sources.model import FeedItem
from my_feed.log import logger
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
    # store JSON as strings, these are only used on the frontend anyways
    tags: str = Field(default=r"[]")  # List[str]
    data: Optional[bytes] = Field(default=None)  # Dict[str, Any]

    # dates
    when: datetime
    release_date: Optional[date] = Field(default=None)

    # urls
    image_url: Optional[str] = Field(default=None)
    url: Optional[str] = Field(default=None)


feed_engine = create_engine(
    settings.SQLITE_DB_PATH,
    echo=settings.SQL_ECHO,
)


def init_db() -> None:
    logger.info("Creating tables...")
    SQLModel.metadata.create_all(feed_engine)


def _list_pickle_files() -> list[Path]:
    return sorted(
        Path(settings.SCAN_INPUT_DIR).glob("*.pickle"), key=lambda p: p.stat().st_mtime
    )


def load_pickled_feeditems() -> Iterator[FeedItem]:
    for f in _list_pickle_files():
        logger.info(f"Loading from '{f}'...")
        with open(f, mode="rb") as fb:
            items = pickle.load(fb)
        assert isinstance(items, list), "Loaded items isnt a list"
        assert len(items) > 0, "No items loaded"
        assert isinstance(items[0], FeedItem), "First loaded item isn't a FeedItem"
        yield from items


def prune_pickle_files() -> None:
    old_files = _list_pickle_files()[:-1]
    if len(old_files):
        for f in old_files:
            logger.info(f"Removing old pickle file: '{f}'")
            f.unlink()


def _model_ids() -> set[str]:
    with Session(feed_engine) as sess:
        model_ids: set[str] = set()
        for model_id in sess.exec(select(FeedModel.model_id)):
            model_ids.add(model_id)
        return model_ids


def import_pickled_data() -> None:
    added = 0
    with Session(feed_engine) as sess:
        model_ids = _model_ids()
        logger.info(f"{len(model_ids)} feed items already in the database")
        for f in load_pickled_feeditems():
            if f.id not in model_ids:
                fm = FeedModel(
                    model_id=f.id,
                    ftype=f.ftype,
                    title=f.title,
                    score=f.score,
                    subtitle=f.subtitle,
                    creator=f.creator,
                    part=f.part,
                    subpart=f.subpart,
                    collection=f.collection,
                    tags=json.dumps(f.tags),
                    data=pickle.dumps(f.data) if bool(f.data) else None,
                    when=f.when,
                    release_date=f.release_date,
                    image_url=f.image_url,
                    url=f.url,
                )
                added += 1
                sess.add(fm)
        sess.flush()
        sess.commit()
    logger.info(f"{added} new items added to the database")


def get_db() -> Generator[Session, None, None]:
    with Session(feed_engine) as session:
        yield session
