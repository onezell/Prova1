from pydantic_settings import BaseSettings


class Settings(BaseSettings):
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

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
