import json
import warnings
from pathlib import Path
from typing import Any, List, NamedTuple
from pydantic import BaseSettings, DirectoryPath, Json, validator, FilePath


class FeedTypes(NamedTuple):
    all: List[str]

    @classmethod
    def from_file(cls, file: Path) -> "FeedTypes":
        with open(file) as f:
            data = json.load(f)
        ft = cls(all=data.get("all", []))

        if len(ft.all) == 0:
            raise ValueError(f"Parsed config from {file} has no ftypes in 'all'")

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
