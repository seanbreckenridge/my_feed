import json
import warnings
from pathlib import Path
from typing import Any, List, NamedTuple
from pydantic import BaseSettings, DirectoryPath, Json, validator, FilePath


class FeedTypes(NamedTuple):
    all: List[str]
    has_scores: List[str]

    @property
    def without_scores(self) -> List[str]:
        hs = set(self.has_scores)
        return [f for f in self.all if f not in hs]

    @classmethod
    def from_file(cls, file: Path) -> "FeedTypes":
        with open(file) as f:
            data = json.load(f)
        ft = cls(all=data.get("all", []), has_scores=data.get("has_scores", []))

        if len(ft.all) == 0:
            raise ValueError(f"Parsed config from {file} has no ftypes in 'all'")

        if len(ft.has_scores) == 0:
            warnings.warn(
                f"Parsed config from {file} has no ftypes in 'has_scores'. This means that no items will be returned when ordered by score."
            )

        return ft


class Settings(BaseSettings):
    SCAN_INPUT_DIR: DirectoryPath
    FEEDTYPES_CONFIG: FilePath
    BEARER_SECRET: str = ""
    BACKEND_CORS_ORIGINS: Json
    SQLITE_DB_URI: str
    SQL_ECHO: bool = True

    @validator("BACKEND_CORS_ORIGINS")
    def validate_cors(cls, v: Any) -> List[str]:
        assert isinstance(v, list)
        for x in v:
            assert isinstance(x, str)
        return v

    def feedtypes(self) -> FeedTypes:
        return FeedTypes.from_file(self.FEEDTYPES_CONFIG)

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

if __name__ == "__main__":
    print(settings.dict())
