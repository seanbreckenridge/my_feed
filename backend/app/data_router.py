import pickle
from typing import Optional, Dict, Any, List, cast
from enum import Enum

import orjson

from fastapi import APIRouter, Depends, Query
from pydantic import validator
from sqlmodel import Session, Field, select
from sqlalchemy import distinct


from app.db import get_db, FeedModel, FeedBase

router = APIRouter()


class FeedRead(FeedBase):  # type: ignore
    # parse from the backend to data structures
    tags: List[str] = Field(default_factory=list)
    data: Dict[str, Any] = Field(default_factory={})

    @validator("tags", pre=True)
    def parse_tags(cls, v: Any) -> List[str]:
        return cast(List[str], orjson.loads(v))

    @validator("data", pre=True)
    def parse_data(cls, v: Any) -> Dict[str, Any]:
        if v is None:
            return {}
        else:
            return cast(Dict[str, Any], pickle.loads(v))


class OrderBy(Enum):
    score = "score"
    when = "when"


class Sort(Enum):
    asc = "asc"
    ascending = "ascending"
    desc = "desc"
    descending = "descending"


# items which shouldn't be shown when sorted by 'score'
# since it'd make the feed too busy
INDIVIDUAL_FEED_TYPES = [
    "anime_episode",
    "manga_chapter",
    "scrobble",
    "trakt_history_episode",
    "trakt_history_movie",
]



@router.get("/types", response_model=List[str])
async def data_types(
    session: Session = Depends(get_db),
) -> List[str]:
    stmt = select(distinct(FeedModel.ftype))
    with session:
        items: List[str] = list(session.exec(stmt))
    return items


@router.get("/", response_model=List[FeedRead])
async def data(
    offset: int = 0,
    limit: int = Query(default=100, lte=100),
    order_by: OrderBy = Query(default=OrderBy.when),
    sort: Sort = Query(default=Sort.desc),
    ftype: Optional[str] = Query(default=None, min_length=2),
    query: Optional[str] = Query(default=None, min_length=2),
    title: Optional[str] = Query(default=None, min_length=2),
    creator: Optional[str] = Query(default=None, min_length=2),
    subtitle: Optional[str] = Query(default=None, min_length=2),
    session: Session = Depends(get_db),
) -> List[FeedRead]:
    stmt = select(FeedModel)
    if ftype is not None and ftype.strip():
        if parts := ftype.strip().split(","):
            stmt = stmt.filter(FeedModel.ftype.in_(parts))  # type: ignore

    if query is None:
        if title:
            stmt = stmt.filter(FeedModel.title.ilike(f"%{title}%"))  # type: ignore
        if creator:
            stmt = stmt.filter(FeedModel.creator.ilike(f"%{creator}%"))  # type: ignore
        if subtitle:
            stmt = stmt.filter(FeedModel.subtitle.ilike(f"%{subtitle}%"))  # type: ignore
    else:
        stmt = stmt.filter(
            (FeedModel.title.ilike(f"%{query}%"))  # type: ignore
            | (FeedModel.creator.ilike(f"%{query}%"))  # type: ignore
            | (FeedModel.subtitle.ilike(f"%{query}%"))  # type: ignore
            | (FeedModel.model_id.ilike(f"%{query}%"))  # type: ignore
        )
    if order_by == OrderBy.score:
        stmt = stmt.filter(FeedModel.score != None)
        stmt = stmt.filter(FeedModel.ftype.notin_(INDIVIDUAL_FEED_TYPES))  # type: ignore
        # ORDER BY Score [CHOSEN], When DESC to show things I completed recently higher when sorting by score
        stmt = stmt.order_by(FeedModel.score.asc() if sort == Sort.asc else FeedModel.score.desc(), FeedModel.when.desc())  # type: ignore
    else:
        stmt = stmt.order_by(FeedModel.when.asc() if sort == Sort.asc else FeedModel.when.desc())  # type: ignore
    stmt = stmt.limit(limit).offset(offset)
    with session:
        items: List[FeedModel] = list(session.exec(stmt))
    return items
