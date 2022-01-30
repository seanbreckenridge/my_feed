from typing import Any, List
from pydantic import BaseSettings, DirectoryPath, Json, validator


class Settings(BaseSettings):
    SCAN_INPUT_DIR: DirectoryPath
    BACKEND_CORS_ORIGINS: Json

    @validator("BACKEND_CORS_ORIGINS")
    def validate_cors(cls, v: Any) -> List[str]:
        assert isinstance(v, list)
        for x in v:
            assert isinstance(x, str)
        return v

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()

if __name__ == "__main__":
    print(settings.dict())
