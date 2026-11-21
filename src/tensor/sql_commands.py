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
