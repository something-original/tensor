"""Конфигурация приложения.

Настройки читаются из переменных окружения. Файл `.env` в корне проекта
подхватывается автоматически, поэтому параметры подключения можно не
передавать в командной строке.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DB_USER=os.getenv("DB_USER", "tensor"),
DB_PASSWORD=os.getenv("DB_PWD", "tensor"),
db_host=os.getenv("DB_HOST", "127.0.0.1"),
db_port=int(os.getenv("DB_PORT", "3333")),
db_name=os.getenv("DB_NAME", "tensor"),
FILE_PATH = os.getenv("FILE_PATH", "data/people.json")
ROOT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Settings:
    """Параметры подключения к PostgreSQL и путь к JSON-файлу с данными."""

    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str
    data_file: Path

    @property
    def connection_params(self) -> dict[str, str | int]:
        """Возвращает именованные аргументы для ``psycopg2.connect``."""
        return {
            "dbname": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
            "host": self.db_host,
            "port": self.db_port,
        }


def load_settings() -> Settings:
    """Собирает настройки приложения из переменных окружения.

    Значения по умолчанию соответствуют локальной базе из README.
    Путь к JSON-файлу можно переопределить переменной ``DATA_FILE``.
    """
    data_file = Path(os.getenv("DATA_FILE", ROOT_DIR / "data" / "people.json"))
    if not data_file.is_absolute():
        data_file = ROOT_DIR / data_file

    return Settings(
        db_user=os.getenv("DB_USER", "tensor"),
        db_password=os.getenv("DB_PWD", "tensor"),
        db_host=os.getenv("DB_HOST", "127.0.0.1"),
        db_port=int(os.getenv("DB_PORT", "3333")),
        db_name=os.getenv("DB_NAME", "tensor"),
        data_file=data_file,
    )
