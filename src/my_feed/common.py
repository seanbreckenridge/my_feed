from datetime import datetime


def _remove_tz(dt: datetime) -> datetime:
    return datetime.fromtimestamp(dt.timestamp())
