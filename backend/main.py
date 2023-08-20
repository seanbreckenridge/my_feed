from typing import Set
from pathlib import Path

import click


@click.group()
def main():
    pass


def glob_database_files(source_database: Path) -> Set[Path]:
    """
    List any of the temporary database files (and the database itself)
    """
    files: Set[Path] = {source_database}
    for temp_db_file in source_database.parent.glob(source_database.name + "-*"):
        files.add(temp_db_file)
    return files


def get_database_path_from_uri(uri: str) -> Path:
    """
    Get the database path from a sqlite3 URI using SQLAlchemy
    """
    from sqlalchemy.engine.url import make_url

    url = make_url(uri)
    if url.drivername != "sqlite":
        raise ValueError("Only SQLite is supported")

    assert url.database is not None
    return Path(url.database)


@main.command()
@click.option(
    "--delete-db",
    is_flag=True,
    help="Delete the database before updating",
    default=False,
)
def update_db(delete_db: bool) -> None:
    """Update the database."""
    from app.db import init_db
    from app.load_json import update_data

    if delete_db:
        from app.settings import settings

        db = get_database_path_from_uri(settings.SQLITE_DB_URI)
        if db.exists():
            assert db.is_file()

        click.echo(f"Deleting database {db}", err=True)
        for file in glob_database_files(db):
            click.echo(f"Deleting {file}", err=True)
            file.unlink(missing_ok=True)

    init_db()
    count = update_data()

    # last line on stdout is the count
    click.echo(count)


if __name__ == "__main__":
    main()
