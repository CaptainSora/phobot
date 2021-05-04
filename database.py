import sqlite3
from datetime import datetime

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
    create_connection()
    sql_add_task = (
        "INSERT INTO tasks(task_name, task_team, assigned_to, due_date) "
        "VALUES(?,?,?,?)"
    )
    values = (name, team, ','.join(assigned), due)
    create_connection()
    CONN.execute(sql_add_task, values)
    CONN.commit()

def complete_task(task_id):
    create_connection()
    sql_complete_task = (
        "UPDATE tasks SET complete_date = ? WHERE task_id = ?"
    )
    comp_time = datetime.now().strftime("%b %d, %H:%M")
    values = (comp_time, task_id)
    CONN.execute(sql_complete_task, values)
    CONN.commit()

def remove_task(task_id):
    create_connection()
    sql_delete_task = (
        "DELETE FROM tasks WHERE task_id = ?"
    )
    values = (task_id,)
    CONN.execute(sql_delete_task, values)
    CONN.commit()


def get_tasks(sel="*", ext=""):
    create_connection()
    sql_get_tasks = (
        f"SELECT {sel} FROM tasks {ext}"
    )
    return CONN.execute(sql_get_tasks).fetchall()

# def temp_sql():
#     create_connection()
#     sql_modify_time = (
#         "UPDATE tasks SET due_date = ? WHERE task_id = ?"
#     )
#     values = [
#         ("May 5, 23:59", 10),
#         ("May 9, 23:59", 14),
#         ("May 3, 23:59", 15),
#         ("May 4, 23:59", 16),
#         ("May 7, 23:59", 17),
#     ]
#     CONN.executemany(sql_modify_time, values)
#     CONN.commit()

# temp_sql()
