from typing import Set
from pathlib import Path

import click


@click.group()
def main():
    pass


@main.command()
@click.option(
    "--clear-db",
    is_flag=True,
    help="Delete the database before updating",
    default=False,
)
@click.option(
    "-C",
    "--write-count-to",
    type=click.Path(exists=False, dir_okay=False, writable=True),
    help="Write how many items were added to this file",
)
def update_db(clear_db: bool, write_count_to: str) -> None:
    """Update the database."""
    from app.db import init_db, Session, feed_engine
    from app.load_json import update_data

    if clear_db:
        # remove all rows from the database
        with Session(feed_engine) as session:
            # run a raw SQL query
            session.execute("DELETE FROM feedmodel WHERE 1=1")
            session.commit()


    init_db()
    count = update_data()

    if write_count_to is not None:
        with open(write_count_to, "w") as f:
            f.write(str(count))


if __name__ == "__main__":
    main()
