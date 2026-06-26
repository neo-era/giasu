from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Cấu hình đọc từ biến môi trường / .env.

    NFR-30: mọi khóa LLM chỉ tồn tại ở backend, đọc từ env — KHÔNG hardcode,
    KHÔNG gửi ra client.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://giasu:giasu@localhost:5432/giasu"
    cors_origins: list[str] = ["http://localhost:3000"]

    # Khóa nhà cung cấp LLM (điền ở .env, không commit)
    llm_api_key_primary: str = ""
    llm_api_key_secondary: str = ""


settings = Settings()
