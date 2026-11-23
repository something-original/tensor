"""Синхронная работа с PostgreSQL: подключение, инициализация и выборки."""

import logging
from pathlib import Path

import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import RealDictCursor

from ...config import Settings
from .importer import insert_employees, load_employees
from .sql_commands import (
    COUNT_EMPLOYEES,
    CREATE_EMPLOYEES_TABLE,
    CREATE_PARENT_ID_INDEX,
    SELECT_COLLEAGUES_BY_EMPLOYEE_ID,
    SELECT_EMPLOYEE_BY_ID,
    TRUNCATE_EMPLOYEES,
)

logger = logging.getLogger(__name__)


def connect(settings: Settings) -> connection:
    """Открывает синхронное подключение к PostgreSQL."""
    return psycopg2.connect(**settings.connection_params)


def init_database(
    conn: connection,
    file_path: Path,
    reset: bool = False,
) -> int:
    """Готовит базу к работе и возвращает число импортированных записей.

    Создаёт таблицу и индекс, затем заполняет таблицу данными из JSON,
    если она пуста. При ``reset=True`` таблица предварительно очищается,
    чтобы данные можно было перезалить.

    Очистка и импорт выполняются в одной транзакции: если JSON окажется
    некорректным, старая таблица останется нетронутой.
    """
    with conn, conn.cursor() as cursor:
        cursor.execute(CREATE_EMPLOYEES_TABLE)
        cursor.execute(CREATE_PARENT_ID_INDEX)

        if reset:
            cursor.execute(TRUNCATE_EMPLOYEES)
        else:
            cursor.execute(COUNT_EMPLOYEES)
            if cursor.fetchone()[0] > 0:
                logger.info("Таблица employees уже заполнена, импорт пропущен")
                return 0

        employees = load_employees(file_path)
        imported = insert_employees(cursor, employees)

    if reset:
        logger.info("Таблица employees очищена и заполнена заново")
    logger.info("Импортировано записей: %s", imported)
    return imported


def fetch_employee(conn: connection, employee_id: int) -> dict | None:
    """Возвращает запись сотрудника по идентификатору или ``None``."""
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute(SELECT_EMPLOYEE_BY_ID, {"employee_id": employee_id})
        row = cursor.fetchone()

    return dict(row) if row is not None else None


def fetch_colleagues(conn: connection, employee_id: int) -> list[str]:
    """Возвращает имена всех сотрудников офиса, где работает сотрудник.

    Если запись с таким ``employee_id`` отсутствует или у неё нет
    офиса-предка, возвращается пустой список.
    """
    with conn.cursor() as cursor:
        cursor.execute(SELECT_COLLEAGUES_BY_EMPLOYEE_ID, {"employee_id": employee_id})
        rows = cursor.fetchall()

    return [row[0] for row in rows]
