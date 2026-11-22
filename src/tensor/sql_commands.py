create_empolyees_table = """
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        parent_id INTEGER,
        name VARCHAR NOT NULL,
        type INTEGER NOT NULL
    );
"""

get_employees_count = """
    SELECT COUNT(*) FROM employees AS employees_count;
"""

insert_employees_data = """
    INSERT INTO employees("id", "parent_id", "name", "type") VALUES {values_clause};
"""

select_people_by_id = """
    WITH
        offices AS (SELECT id FROM employees WHERE "type" = 1),
        departments AS (SELECT id, parent_id FROM employees WHERE "type" = 2),
        people AS (SELECT id, parent_id, name FROM empolyees WHERE "type" = 3)
        department_id AS (SELECT parent_id FROM employees WHERE id = {employee_id})
"""
