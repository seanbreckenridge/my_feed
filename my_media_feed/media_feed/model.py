from typing import Optional, Union, List
from datetime import datetime, date

from dataclasses import dataclass, field

Tags = List[str]
DateIsh = Union[datetime, date]


@dataclass
class FeedItem:
    id: str  # unique id, namespaced by module
    # if it has one, parent entity (e.g. scrobble -> album, or episode -> tv show)
    title: str  # name of entry, track, episode name, or 'Episode {}'
    media_type: str  # scrobble, episode
    when: DateIsh  # when I finished this
    tags: Tags = field(default_factory=list)  # extra information/tags for this item
    # artist, or person who created this
    creators: List[str] = field(default_factory=list)
    part: Optional[int] = None  # e.g. season
    subpart: Optional[int] = None  # e.g. episode, or track number
    parent_id: Optional[str] = None
    subtitle: Optional[str] = None  # show name, or album name
    url: Optional[str] = None
    image_url: Optional[str] = None
    score: Optional[float] = None  # normalized to out of 10
