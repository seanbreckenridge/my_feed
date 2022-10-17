import json
import pickle
from pathlib import Path
from typing import Iterator

from sqlmodel import Session, select  # type: ignore[import]
from my_feed.sources.model import FeedItem

from app.db import FeedModel, logger, feed_engine
from app.settings import settings


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


def prune_pickle_files(remove_all: bool = False) -> None:
    if remove_all:
        old_files = _list_pickle_files()
    else:
        # remove all but last file (sorted by mod time)
        old_files = _list_pickle_files()[:-1]
    if len(old_files):
        for f in old_files:
            logger.info(f"Removing old pickle file: '{f}'")
            f.unlink()


def _model_ids() -> set[str]:
    model_ids: set[str] = set()
    with Session(feed_engine) as sess:
        for model_id in sess.exec(select(FeedModel.model_id)):
            model_ids.add(model_id)
    return model_ids


def import_pickled_data() -> int:
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
                    when=int(f.when.timestamp()),
                    release_date=f.release_date,
                    image_url=f.image_url,
                    url=f.url,
                )
                sess.add(fm)
                added += 1
        sess.flush()
        sess.commit()
    logger.info(f"{added} new items added to the database")
    return added


def update_data() -> int:

    added = 0
    try:
        added = import_pickled_data()
    except Exception as e:
        logger.exception(str(e), exc_info=e)
        logger.warning("Found broken files, removing all pickled data files...")
        # if this failed, pickle files may have failed to upload properly, so
        # we should remove all pickle files
        prune_pickle_files(remove_all=True)
    else:
        prune_pickle_files()
    return added
