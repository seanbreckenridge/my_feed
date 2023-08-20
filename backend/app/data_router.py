from typing import Optional, Dict, Any, List, cast
from enum import Enum

import orjson

from fastapi import APIRouter, Depends, Query
from pydantic import validator
from sqlmodel import Session, Field, select  # type: ignore[import]
from sqlalchemy import distinct  # type: ignore[import]

from app.token import bearer_auth
from app.db import get_db, FeedModel, FeedBase
from app.settings import settings

router = APIRouter()


class FeedRead(FeedBase):
    # parse from the backend to data structures
    data: Dict[str, Any] = Field(default_factory=dict)
    flags: List[str] = Field(default_factory=list)

    @validator("flags", pre=True)
    def parse_flags(cls, v: Any) -> List[str]:
        if v is None:
            return []
        else:
            return cast(List[str], orjson.loads(v))

    @validator("data", pre=True)
    def parse_data(cls, v: Any) -> Dict[str, Any]:
        if v is None:
            return {}
        else:
            return cast(Dict[str, Any], orjson.loads(v))


class OrderBy(Enum):
    score = "score"
    when = "when"
    release = "release"


class Sort(Enum):
    asc = "asc"
    desc = "desc"


@router.get("/types", response_model=List[str])
async def data_types(
    session: Session = Depends(get_db),
) -> List[str]:
    stmt = select(distinct(FeedModel.ftype))  # type: ignore[call-overload]
    with session:
        items: List[str] = list(session.exec(stmt))
    return items


feedtypes = settings.feedtypes()

@router.get("/", response_model=List[FeedRead])
async def data(
    offset: int = 0,
    limit: int = Query(default=100, gt=0, lt=501),
    order_by: OrderBy = Query(default=OrderBy.when),
    sort: Sort = Query(default=Sort.desc),
    ftype: Optional[str] = Query(default=None, min_length=2),
    query: Optional[str] = Query(default=None, min_length=2),
    session: Session = Depends(get_db),
) -> List[FeedRead]:
    stmt = select(FeedModel)
    if ftype is not None and ftype.strip():
        if parts := ftype.strip().split(","):
            stmt = stmt.filter(FeedModel.ftype.in_(parts))  # type: ignore

    if query is not None and query.strip():
        stmt = stmt.filter(
            (FeedModel.title.ilike(f"%{query}%"))  # type: ignore
            | (FeedModel.creator.ilike(f"%{query}%"))  # type: ignore
            | (FeedModel.subtitle.ilike(f"%{query}%"))  # type: ignore
            | (FeedModel.model_id.ilike(f"%{query}%"))  # type: ignore
        )
    if order_by == OrderBy.score:
        stmt = stmt.filter(FeedModel.score is not None and FeedModel.score > 0)
        # ORDER BY Score [CHOSEN], When DESC to show things I completed recently higher when sorting by score
        stmt = stmt.order_by(FeedModel.score.asc() if sort == Sort.asc else FeedModel.score.desc(), FeedModel.when.desc())  # type: ignore
    elif order_by == OrderBy.when:
        stmt = stmt.order_by(FeedModel.when.asc() if sort == Sort.asc else FeedModel.when.desc())  # type: ignore
    elif order_by == OrderBy.release:
        stmt = stmt.filter(FeedModel.release_date is not None)
        stmt = stmt.order_by(
            FeedModel.release_date.asc()
            if sort == Sort.asc
            else FeedModel.release_date.desc()
        )
    stmt = stmt.limit(limit).offset(offset)
    with session:
        items: List[FeedModel] = list(session.exec(stmt))
    # fastapi handles converting from FeedModel to FeedRead
    return cast(List[FeedRead], items)


@router.get("/ids")
def data_ids(
    session: Session = Depends(get_db),
    token: str = Depends(bearer_auth),
) -> List[str]:
    stmt = select(FeedModel.model_id)
    with session:
        items: List[str] = list(session.exec(stmt))
    return items
