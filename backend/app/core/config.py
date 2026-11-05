from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "HEAT-EWS"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api"
    TIMEZONE: str = "Asia/Dubai"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # Open-Meteo API Endpoints
    OPEN_METEO_WEATHER_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_AIR_QUALITY_URL: str = "https://air-quality-api.open-meteo.com/v1/air-quality"

    # Security
    SECRET_KEY: str = "replace-with-a-long-random-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Analytics & Privacy Thresholds (from SRS v3.0)
    BASELINE_DAYS: int = 14
    ALERT_COOLDOWN_HOURS: int = 24
    SMALL_CELL_SUPPRESSION_THRESHOLD: int = 10

    # UAE MOHRE Midday Break: 12:30 to 15:00, 15 June - 15 September
    MOHRE_BREAK_START_HOUR: float = 12.5
    MOHRE_BREAK_END_HOUR: float = 15.0
    MOHRE_BREAK_START_MONTH: int = 6
    MOHRE_BREAK_START_DAY: int = 15
    MOHRE_BREAK_END_MONTH: int = 9
    MOHRE_BREAK_END_DAY: int = 15

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        extra="ignore"
    )


settings = Settings()
