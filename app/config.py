"""Configuration settings for ERPNext WhatsApp CRM Gateway."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "ERPNext WhatsApp CRM Gateway"
    DEBUG: bool = False
    PORT: int = 8080

    # ERPNext Settings
    ERPNEXT_URL: str = "http://localhost:8000"
    ERPNEXT_API_KEY: str = "your_erpnext_api_key"
    ERPNEXT_API_SECRET: str = "your_erpnext_api_secret"

    # WhatsApp Cloud API Settings
    WHATSAPP_TOKEN: str = "your_meta_system_user_token"
    WHATSAPP_PHONE_NUMBER_ID: str = "your_phone_number_id"
    WHATSAPP_VERIFY_TOKEN: str = "erpnext_secret_verify_token"
    META_GRAPH_VERSION: str = "v18.0"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
