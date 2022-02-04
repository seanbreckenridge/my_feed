from typing import Optional, Dict, Any, List, cast
from enum import Enum
import pickle

import orjson

from fastapi import APIRouter, Depends, Query
from pydantic import validator
from sqlmodel import Session, Field, select, func
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
    query: Optional[str] = Query(default=None, min_length=2),
    title: Optional[str] = Query(default=None, min_length=2),
    creator: Optional[str] = Query(default=None, min_length=2),
    subtitle: Optional[str] = Query(default=None, min_length=2),
    session: Session = Depends(get_db),
) -> List[FeedRead]:
    stmt = select(FeedModel)
    if query is None:
        if title:
            stmt = stmt.filter(FeedModel.title.ilike(f"%{title}%"))  # type: ignore
        if creator:
            stmt = stmt.filter(FeedModel.creator.ilike(f"%{creator}%"))  # type: ignore
        if subtitle:
            stmt = stmt.filter(FeedModel.subtitle.ilike(f"%{subtitle}%"))  # type: ignore
    else:
        stmt = stmt.filter(
            (FeedModel.title.ilike(f"%{query}"))  # type: ignore
            | (FeedModel.creator.ilike(f"%{query}%"))  # type: ignore
            | (FeedModel.subtitle.ilike(f"%{query}%"))  # type: ignore
        )
    order_field = FeedModel.when if order_by == OrderBy.when else FeedModel.score
    order_func = order_field.desc() if sort == Sort.desc else order_field.asc()  # type: ignore
    stmt = stmt.order_by(order_func).offset(offset).limit(limit)
    with session:
        items: List[FeedModel] = list(session.exec(stmt))
    return items
