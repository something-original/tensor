import argparse
import json
import sys
import logging

import psycopg2
from psycopg2.extras import execute_values

from config import DB_URL, FILE_PATH
from sql_commands import (
    CREATE_TABLE,
    CREATE_INDEX,
    COUNT_EMPLOYEES,
    INSERT_EMPLOYEES,
    SELECT_EMPLOYEE_TYPE,
    SELECT_COLLEAGUES
)

logger = logging.getLogger(__name__)


def configure_logging() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stdout,
    )


def main() -> int:
    """Основная функция консольного приложения.
    Инициализирует таблицу и выполняет парсинг приложенного json-файла, если таблица не содержит данных.
    Принимает в качестве аргумента id сотрудников и выводит в консоль список фамилий в качестве ответа или сообщение об ошибке.

    Returns:
        int: код ошибки (0, если успешно; 1, если произошла ошибка)
    """
    configure_logging()

    parser = argparse.ArgumentParser(description="Сотрудники офиса по id сотрудника")
    parser.add_argument("--employee_id", type=int, required=False, help="идентификатор сотрудника")
    parser.add_argument("--reset", action="store_true", help="перезалить данные из JSON")
    args = parser.parse_args()

    with psycopg2.connect(DB_URL) as connection, connection.cursor() as cursor:
        logger.info("Создаем таблицу, если не существует")
        cursor.execute(CREATE_TABLE)

        logger.info("Создаем индекс, если не существует")
        cursor.execute(CREATE_INDEX)

        if args.reset:
            logger.info("Очищаем таблицу")
            cursor.execute("TRUNCATE employees;")
            return 0

        cursor.execute(COUNT_EMPLOYEES)
        num_employees = cursor.fetchone()[0]
        logger.info(f"Сотрудников в таблице: {num_employees}")

        if num_employees > 0:
            logger.info("Пропускаем заполнение")
        else:
            logger.info("Парсим файл")

            with open(FILE_PATH, encoding="utf-8-sig") as file:
                employees = [
                    (row["id"], row["ParentId"], row["Name"], row["Type"])
                    for row in json.load(file)
                ]

            execute_values(cursor, INSERT_EMPLOYEES, employees)
            logger.info("Таблица заполнена")

        def process_employee(employee_id: int) -> int:
            cursor.execute(SELECT_EMPLOYEE_TYPE, (employee_id,))
            employee = cursor.fetchone()

            if employee is None:
                logger.error(f"Сотрудник с id={employee_id} не найден")
                return 1
            if employee[0] != 3:
                logger.error(f"Запись с id={employee_id} не является сотрудником")
                return 1

            cursor.execute(SELECT_COLLEAGUES, (employee_id,))
            for (name,) in cursor.fetchall():
                print(name)

            return 0

        if args.employee_id is not None:
            return process_employee(args.employee_id)

        try:
            while True:
                user_input = input("Введите id сотрудника\n")
                try:
                    employee_id = int(user_input)
                except ValueError:
                    logger.error(f"Некорректный ввод: {user_input}")
                    continue
                process_employee(employee_id)
        except KeyboardInterrupt:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
