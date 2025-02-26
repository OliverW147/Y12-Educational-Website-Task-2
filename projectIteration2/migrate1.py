import sqlite3

def add_column_if_not_exists(db_name, table_name, column_name, column_type):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [column[1] for column in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
        print(f"Column '{column_name}' added to the '{table_name}' table.")
    else:
        print(f"Column '{column_name}' already exists in the '{table_name}' table.")
    conn.commit()
    conn.close()

add_column_if_not_exists('site.db', 'resources', 'link', 'TEXT')
add_column_if_not_exists('site.db', 'resources', 'more_links', 'TEXT')
