from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration and environment variables."""

    # Default output file location
    output_file: str = "output.json"

    # Default target URL as defined in the task
    target_url: str = "https://www2.hm.com/bg_bg/productpage.1274171042.html"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Expose a singleton instance for use throughout the app
settings = Settings()
