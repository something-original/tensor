"""SQL-запросы приложения.

Запросы вынесены в отдельный модуль, чтобы их было удобно читать,
анализировать и оптимизировать независимо от Python-кода.
"""

CREATE_EMPLOYEES_TABLE = """
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        parent_id INTEGER,
        name TEXT NOT NULL,
        type SMALLINT NOT NULL CHECK (type IN (1, 2, 3))
    );
"""

# Индекс по parent_id нужен рекурсивным запросам: без него каждый шаг
# обхода дерева превращается в последовательное сканирование таблицы.
CREATE_PARENT_ID_INDEX = """
    CREATE INDEX IF NOT EXISTS employees_parent_id_idx
        ON employees (parent_id);
"""

COUNT_EMPLOYEES = """
    SELECT COUNT(*) FROM employees;
"""

TRUNCATE_EMPLOYEES = """
    TRUNCATE TABLE employees;
"""

# Шаблон для psycopg2.extras.execute_values: %s подставляет список кортежей.
INSERT_EMPLOYEES = """
    INSERT INTO employees (id, parent_id, name, type) VALUES %s;
"""

SELECT_EMPLOYEE_BY_ID = """
    SELECT id, parent_id, name, type
    FROM employees
    WHERE id = %(employee_id)s;
"""

# 1. ancestors — поднимаемся от сотрудника вверх по parent_id до офиса (type = 1).
# 2. office — находим идентификатор этого офиса.
# 3. office_tree — спускаемся от офиса вниз по всему поддереву.
# 4. Из поддерева выбираем только сотрудников (type = 3).
#
# Ограничение depth защищает от зацикливания, если в данных окажется цикл
# (в PostgreSQL 10 клауза CYCLE ещё недоступна).
SELECT_COLLEAGUES_BY_EMPLOYEE_ID = """
    WITH RECURSIVE ancestors AS (
        SELECT id, parent_id, type, 0 AS depth
        FROM employees
        WHERE id = %(employee_id)s

        UNION ALL

        SELECT e.id, e.parent_id, e.type, a.depth + 1
        FROM employees AS e
        JOIN ancestors AS a ON e.id = a.parent_id
        WHERE a.type <> 1
          AND a.depth < 100
    ),
    office AS (
        SELECT id
        FROM ancestors
        WHERE type = 1
        LIMIT 1
    ),
    office_tree AS (
        SELECT id, parent_id, name, type, 0 AS depth
        FROM employees
        WHERE id IN (SELECT id FROM office)

        UNION ALL

        SELECT e.id, e.parent_id, e.name, e.type, t.depth + 1
        FROM employees AS e
        JOIN office_tree AS t ON e.parent_id = t.id
        WHERE t.depth < 100
    )
    SELECT name
    FROM office_tree
    WHERE type = 3
    ORDER BY id;
"""
