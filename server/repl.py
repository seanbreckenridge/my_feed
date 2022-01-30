#!/usr/bin/env python3
from app.db import FeedModel, get_db
from sqlmodel import select  # type: ignore[import]

[sess] = list(get_db())

print("Use 'sess' for the current database session")

import IPython  # type: ignore[import]

IPython.embed()
