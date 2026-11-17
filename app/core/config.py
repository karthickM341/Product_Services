from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Product Service"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "product_service"
    DB_USER: str = "product_user"
    DB_PASSWORD: str = "change_me"
    DB_URL: str | None = None
    SQL_ECHO: bool = False

    @property
    def database_url(self) -> str:
        if self.DB_URL:
            return self.DB_URL
        from urllib.parse import quote_plus
        return (
            f"mysql+pymysql://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
