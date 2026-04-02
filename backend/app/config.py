from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./data/emails.db"

    # Auth
    admin_username: str = "admin"
    admin_password: str = "changeme"
    jwt_secret: str = "change-this-secret-in-production"
    jwt_expire_minutes: int = 480  # 8 hours
    jwt_refresh_expire_minutes: int = 10080  # 7 days

    # IMAP
    imap_host: str = "imap.gmail.com"
    imap_port: int = 993
    imap_user: str = ""
    imap_password: str = ""

    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # OpenAI-compatible API
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # Classification categories
    categories: list[str] = [
        "richiesta_info",
        "reclamo",
        "supporto_tecnico",
        "preventivo",
        "collaborazione",
        "spam",
        "altro",
    ]

    # Polling
    polling_enabled: bool = False
    polling_interval_seconds: int = 300  # 5 minutes

    # Approval workflow
    auto_approve_threshold: float = 0.0  # 0 = disabled, e.g. 0.9 = auto-approve above 90%

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
