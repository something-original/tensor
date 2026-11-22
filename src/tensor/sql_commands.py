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
    WITH RECURSIVE employee_hierarchy AS (
        SELECT id, parent_id, name, type
        FROM employees
        WHERE id = :employee_id

        UNION ALL

        SELECT e.id, e.parent_id, e.name, e.type
        FROM employees e
        INNER JOIN employee_hierarchy eh ON e.id = eh.parent_id
        WHERE eh.type != 1
    ),
    office AS (
        SELECT id FROM employee_hierarchy WHERE type = 1
    ),
    all_employees_in_office AS (

        SELECT id, parent_id, name, type
        FROM employees
        WHERE id = (SELECT id FROM office)

        UNION ALL

        SELECT e.id, e.parent_id, e.name, e.type
        FROM employees e
        INNER JOIN all_employees_in_office aeo ON e.parent_id = aeo.id
    )
    SELECT name FROM all_employees_in_office WHERE "type" = 3;
    """
