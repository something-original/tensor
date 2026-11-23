"""Консольный интерфейс приложения."""

import argparse
import logging
import sys
from contextlib import closing

import psycopg2

from ...config import Settings, load_settings
from .db import connect, fetch_colleagues, fetch_employee, init_database

logger = logging.getLogger(__name__)

# Тип записи «сотрудник»: только для него имеет смысл искать коллег по офису.
EMPLOYEE_TYPE = 3


def build_argument_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="tensor",
        description=(
            "Выводит список сотрудников офиса, в котором работает "
            "сотрудник с указанным идентификатором."
        ),
    )
    parser.add_argument(
        "employee_id",
        nargs="?",
        type=int,
        metavar="ID",
        help="идентификатор сотрудника (если не указан, будет запрошен ввод)",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="очистить таблицу employees и заново импортировать данные из JSON",
    )
    return parser


def configure_logging() -> None:
    """Настраивает логирование в stderr, чтобы не засорять stdout."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )


def ask_employee_id() -> int:
    """Запрашивает идентификатор сотрудника в интерактивном режиме."""
    while True:
        raw_value = input("Введите id сотрудника: ").strip()
        if raw_value.isdigit() and int(raw_value) > 0:
            return int(raw_value)

        print("id должен быть целым положительным числом.", file=sys.stderr)


def run(settings: Settings, employee_id: int, reset: bool) -> int:
    """Выполняет основной сценарий и возвращает код завершения.

    Коды завершения: 0 — успех, 1 — сотрудник не найден или нет офиса,
    2 — переданный id не является сотрудником.
    """
    with closing(connect(settings)) as conn:
        init_database(conn, settings.data_file, reset=reset)

        employee = fetch_employee(conn, employee_id)
        if employee is None:
            logger.error("Сотрудник с id=%s не найден", employee_id)
            return 1

        if employee["type"] != EMPLOYEE_TYPE:
            logger.error(
                "Запись с id=%s не является сотрудником (type=%s)",
                employee_id,
                employee["type"],
            )
            return 2

        colleagues = fetch_colleagues(conn, employee_id)

    if not colleagues:
        logger.error("Для сотрудника с id=%s не найдено коллег по офису", employee_id)
        return 1

    for name in colleagues:
        print(name)

    return 0


def main(argv: list[str] | None = None) -> int:
    """Точка входа консольного приложения."""
    configure_logging()
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    employee_id = args.employee_id
    if employee_id is None:
        try:
            employee_id = ask_employee_id()
        except EOFError:
            parser.error("идентификатор сотрудника не передан")

    if employee_id <= 0:
        parser.error("идентификатор сотрудника должен быть положительным числом")

    try:
        return run(load_settings(), employee_id, args.reset)
    except psycopg2.Error as error:
        logger.error("Ошибка PostgreSQL: %s", error)
        logger.error("Проверьте параметры подключения и доступность базы (см. README.md)")
        return 1
    except (OSError, ValueError) as error:
        logger.error("Не удалось прочитать данные: %s", error)
        return 1
