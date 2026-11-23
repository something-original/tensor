CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        parent_id INTEGER,
        name TEXT NOT NULL,
        type SMALLINT NOT NULL CHECK (type IN (1, 2, 3))
    );
"""

CREATE_INDEX = """
    CREATE INDEX IF NOT EXISTS employees_parent_id_idx ON employees (parent_id);
"""

INSERT_EMPLOYEES = """
    INSERT INTO employees (id, parent_id, name, type) VALUES %s;
"""

SELECT_EMPLOYEE_TYPE = """
    SELECT type FROM employees WHERE id = %s;
"""

SELECT_COLLEAGUES = """
    WITH RECURSIVE ancestors AS (
        SELECT id, parent_id, type
        FROM employees
        WHERE id = %s

        UNION ALL

        SELECT e.id, e.parent_id, e.type
        FROM employees AS e
        JOIN ancestors AS a ON e.id = a.parent_id
        WHERE a.type != 1
    ),
    office AS (
        SELECT id FROM ancestors WHERE type = 1 LIMIT 1
    ),
    office_tree AS (
        SELECT id, parent_id, name, type
        FROM employees
        WHERE id IN (SELECT id FROM office)

        UNION ALL

        SELECT e.id, e.parent_id, e.name, e.type
        FROM employees AS e
        JOIN office_tree AS t ON e.parent_id = t.id
    )
    SELECT name
    FROM office_tree
    WHERE type = 3
    ORDER BY name;
"""

COUNT_EMPLOYEES = "SELECT COUNT(*) FROM employees;"
