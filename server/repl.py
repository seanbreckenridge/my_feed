#!/usr/bin/env python3
from app.db import select, FeedModel, get_db

[sess] = list(get_db())

print("Use 'sess' for the current database session")

import IPython

IPython.embed()
