import sqlite3

CONN = None

# DB FUNCTIONS ================================================================

def create_connection():
    global CONN
    if CONN is None:
        CONN = sqlite3.connect('yearbook.db')
        CONN.row_factory = sqlite3.Row

def close_connection():
    if CONN is not None:
        CONN.commit()
        CONN.close()

def create_db():
    create_connection()
    sql_create_tasks = (
        "CREATE TABLE IF NOT EXISTS tasks("
        "task_id INTEGER PRIMARY KEY,"
        "task_name TEXT NOT NULL," # name of the task
        "task_team TEXT," # which team the task is assigned to
        "assigned_to TEXT NOT NULL," # list of pingable IDs, comma-separated
        "due_date TEXT NOT NULL," # python datetime string
        "complete_date TEXT" # NULL for incomplete
        ")"
    )
    CONN.execute(sql_create_tasks)
    CONN.commit()

def insert_task(name, team, assigned, due):
    sql_add_task = (
        "INSERT INTO tasks(task_name, task_team, assigned_to, due_date) "
        "VALUES(?,?,?,?)"
    )
    values = (name, team, ','.join(assigned), due)
    create_connection()
    CONN.execute(sql_add_task, values)
    CONN.commit()

def complete_task(task_id):
    sql_complete_task = (
        "UPDATE tasks SET complete_date = ? WHERE task_id = ?"
    )
    # FIX ME WITH DATE FORMAT
    values = (None, task_id)
    CONN.execute(sql_complete_task, values)
    CONN.commit()

def get_tasks():
    create_connection()
    sql_get_tasks = (
        "SELECT * FROM tasks"
    )
    return CONN.execute(sql_get_tasks).fetchall()
