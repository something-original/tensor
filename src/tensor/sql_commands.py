create_empolyees_table = """
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name VARCHAR NOT NULL
    );
"""

create_departments_table = """
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY,
        name VARCHAR NOT NULL
    );
"""

create_offices_table = """
    CREATE TABLE IF NOT EXISTS offices (
        id INTEGER PRIMARY KEY,
        name VARCHAR NOT NULL
    );
"""

get_tables_count = """
    SELECT
        (SELECT COUNT(*) FROM employees) AS employees_count,
        (SELECT COUNT(*) FROM departments) AS departments_count,
        (SELECT COUNT(*) FROM offices) AS offices_count;
"""
