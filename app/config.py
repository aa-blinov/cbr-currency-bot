from pathlib import Path
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Settings for the application."""

    telegram_token: str = Field(..., json_schema_extra={"env": "TELEGRAM_TOKEN"})

    base_currencies: List[str] = Field(
        ["USD", "EUR", "CNY", "KZT", "KGS", "BYN"],
        json_schema_extra={"env": "BASE_CURRENCIES"},
    )

    log_level: str = Field("INFO", json_schema_extra={"env": "LOG_LEVEL"})
    log_dir: Path = Field(BASE_DIR / "logs", json_schema_extra={"env": "LOG_DIR"})
    log_rotation: str = Field("5 MB", json_schema_extra={"env": "LOG_ROTATION"})

    cbr_api_url: str = Field(
        "https://www.cbr.ru/scripts/XML_daily.asp",
        json_schema_extra={"env": "CBR_API_URL"},
    )

    model_config = {
        "env_file": BASE_DIR / ".env",
        "env_file_encoding": "utf-8",
    }

    @field_validator("base_currencies", mode="before")
    def parse_base_currencies(cls, value):
        """Parses the base currencies from a comma-separated string or JSON array to a list."""
        if isinstance(value, str):
            try:
                import json
                return json.loads(value)
            except json.JSONDecodeError:
                return [currency.strip() for currency in value.split(",")]

        return value


settings = Settings()

settings.log_dir.mkdir(exist_ok=True)
