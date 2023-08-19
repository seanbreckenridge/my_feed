import orjson
from pathlib import Path
from typing import Iterator

from sqlmodel import Session, select  # type: ignore[import]
from my_feed.sources.model import FeedItem

from app.db import FeedModel, logger, feed_engine
from app.settings import settings


def _list_json_files() -> list[Path]:
    return sorted(
        Path(settings.SCAN_INPUT_DIR).glob("*.json"), key=lambda p: p.stat().st_mtime
    )


def load_json_items() -> Iterator[FeedItem]:
    for f in _list_json_files():
        logger.info(f"Loading from '{f}'...")
        with open(f, "r") as ff:
            for line in ff:
                yield FeedItem.from_json(orjson.loads(line))


def prune_json_files(remove_all: bool = False) -> None:
    if remove_all:
        old_files = _list_json_files()
    else:
        # remove all but last file (sorted by mod time)
        old_files = _list_json_files()[:-1]
    if len(old_files):
        for f in old_files:
            logger.info(f"Removing old json file: '{f}'")
            f.unlink()


def _model_ids() -> set[str]:
    model_ids: set[str] = set()
    with Session(feed_engine) as sess:
        for model_id in sess.exec(select(FeedModel.model_id)):
            model_ids.add(model_id)
    return model_ids


def import_json_data() -> int:
    added = 0
    with Session(feed_engine) as sess:
        model_ids = _model_ids()
        logger.info(f"{len(model_ids)} feed items already in the database")
        for f in load_json_items():
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
                    flags=orjson.dumps(f.flags) if len(f.flags) else None,
                    data=orjson.dumps(f.data) if len(f.data) else None,
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
        added = import_json_data()
    except Exception as e:
        logger.exception(str(e), exc_info=e)
        logger.warning("Found broken files, removing all json data files...")
        # if this failed, json files may have failed to upload properly, so
        # we should remove all json files
        prune_json_files(remove_all=True)
    else:
        prune_json_files()
    return added
