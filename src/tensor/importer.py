"""Импорт иерархии сотрудников из JSON-файла в таблицу ``employees``."""

import json
import logging
from pathlib import Path

from psycopg2.extensions import cursor as db_cursor
from psycopg2.extras import execute_values

from .sql_commands import INSERT_EMPLOYEES

logger = logging.getLogger(__name__)

# Поля, без которых запись невозможно корректно вставить в таблицу.
REQUIRED_FIELDS = ("id", "Name", "Type")


def load_employees(file_path: Path) -> list[tuple[int, int | None, str, int]]:
    """Читает JSON-файл и возвращает строки для вставки в таблицу.

    Поля берутся по именам, поэтому порядок ключей в JSON не важен.
    При некорректных данных выбрасывается ``ValueError`` с понятным
    сообщением вместо невнятной ошибки драйвера.
    """
    with file_path.open(encoding="utf-8-sig") as file:
        raw_data = json.load(file)

    if not isinstance(raw_data, list):
        raise ValueError(f"{file_path}: ожидается JSON-массив записей")

    employees: list[tuple[int, int | None, str, int]] = []
    for position, item in enumerate(raw_data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"{file_path}: запись №{position} должна быть объектом")

        missing = [field for field in REQUIRED_FIELDS if field not in item]
        if missing:
            raise ValueError(f"{file_path}: в записи №{position} нет полей {', '.join(missing)}")

        employees.append(
            (
                int(item["id"]),
                item.get("ParentId"),
                str(item["Name"]),
                int(item["Type"]),
            )
        )

    return employees


def insert_employees(
    cursor: db_cursor,
    employees: list[tuple[int, int | None, str, int]],
) -> int:
    """Вставляет записи одной командой и возвращает их число.

    ``execute_values`` формирует один многострочный ``INSERT`` с
    параметрами, поэтому данные не склеиваются в SQL-строку вручную:
    это и быстрее, и безопаснее (нет SQL-инъекций и ошибок на апострофах).
    Транзакцией управляет вызывающий код.
    """
    if not employees:
        logger.warning("Список записей пуст, вставка пропущена")
        return 0

    execute_values(cursor, INSERT_EMPLOYEES, employees)
    return len(employees)
