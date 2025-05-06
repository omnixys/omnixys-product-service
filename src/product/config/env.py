import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Laden Sie die .env-Datei
load_dotenv(dotenv_path=".env")
print("PRODUCT_SERVICE_PORT from .env:", os.getenv("PRODUCT_SERVICE_PORT"))


class Env(BaseSettings):
    PROJECT_NAME: str = "Product Service"
    KC_SERVICE_HOST: str
    KC_SERVICE_PORT: str
    KC_SERVICE_REALM: str
    KC_SERVICE_CLIENT_ID: str
    KC_SERVICE_SECRET: str
    CLIENT_SECRET: str
    APP_ENV: str
    EXCEL_EXPORT_ENABLED: str
    MONGO_DB_USER_NAME: str
    MONGO_DB_USER_PASSWORT: str
    MONGO_DB_URI: str
    MONGO_DB_DATABASE: str
    EXPORT_FORMAT: str
    ZIPKIN_URL: str

    class Config:
        env_file = ".env"  # Stellen Sie sicher, dass dies auf Ihre .env-Datei verweist
        env_file_encoding = "utf-8"
        case_sensitive = True


env = Env()
