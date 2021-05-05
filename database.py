import sqlite3
from datetime import datetime, timedelta

CONN = None

# DB FUNCTIONS

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
    sql_create_reminders = (
        "CREATE TABLE IF NOT EXISTS reminders("
        "rem_id INTEGER PRIMARY KEY,"
        "rem_type INTEGER NOT NULL," # 0 for due reminder, 1 for 1 day reminder
        "task_id INTEGER NOT NULL," # same as tasks
        "task_name TEXT NOT NULL," # same as tasks
        "assigned_to TEXT NOT NULL," # same as tasks
        "rem_date TEXT NOT NULL" # date/time for reminder
        ")"
    )
    CONN.execute(sql_create_tasks)
    CONN.execute(sql_create_reminders)
    CONN.commit()

def insert_task(name, team, assigned, due):
    create_connection()
    assigned_to = ','.join(assigned)
    # Task
    sql_add_task = (
        "INSERT INTO tasks(task_name, task_team, assigned_to, due_date) "
        "VALUES(?,?,?,?)"
    )
    add_values = (name, team, assigned_to, due)
    cur = CONN.execute(sql_add_task, add_values)
    task_id = cur.lastrowid
    # Reminders
    rem_date = datetime.strptime(due, "%b %d, %H:%M") - timedelta(days=1)
    rem_date_str = rem_date.strftime("%b %d, %H:%M")
    sql_add_reminders = (
        "INSERT INTO reminders(rem_type, task_id, task_name, assigned_to, "
        "rem_date) VALUES (?,?,?,?,?)"
    )
    rem_values = [
        (1, task_id, name, assigned_to, rem_date_str),
        (0, task_id, name, assigned_to, due)
    ]
    CONN.executemany(sql_add_reminders, rem_values)
    CONN.commit()
    return task_id

def complete_task(task_id):
    create_connection()
    # Complete task
    sql_complete_task = (
        "UPDATE tasks SET complete_date = ? WHERE task_id = ?"
    )
    comp_time = datetime.now().strftime("%b %d, %H:%M")
    values = (comp_time, task_id)
    CONN.execute(sql_complete_task, values)
    # Remove reminders
    sql_remove_reminders = (
        "DELETE FROM reminders WHERE task_id = ?"
    )
    values = (task_id,)
    CONN.execute(sql_remove_reminders, values)
    CONN.commit()

def remove_task(task_id):
    create_connection()
    # Remove task
    sql_delete_task = (
        "DELETE FROM tasks WHERE task_id = ?"
    )
    values = (task_id,)
    CONN.execute(sql_delete_task, values)
    # Remove reminders
    sql_remove_reminders = (
        "DELETE FROM reminders WHERE task_id = ?"
    )
    CONN.execute(sql_remove_reminders, values)
    CONN.commit()

def remove_reminders(rem_ids):
    create_connection()
    sql_remove_reminders = (
        "DELETE FROM reminders WHERE rem_id = ?"
    )
    values = [(rid,) for rid in rem_ids]
    CONN.executemany(sql_remove_reminders, values)
    CONN.commit()

def get_tasks(sel="*", ext=""):
    create_connection()
    sql_get_tasks = (
        f"SELECT {sel} FROM tasks {ext}"
    )
    return CONN.execute(sql_get_tasks).fetchall()

def get_reminders():
    create_connection()
    sql_get_reminders = "SELECT * FROM reminders"
    return CONN.execute(sql_get_reminders).fetchall()


# def temp_sql():
#     create_connection()
#     sql_modify_team = (
#         "UPDATE tasks SET task_team = ? WHERE task_id = ?"
#     )
#     values = [
#         ("Videography", 8),
#         ("Videography", 9),
#         ("Videography", 10),
#         ("Videography", 71)
#     ]
#     CONN.executemany(sql_modify_team, values)
#     CONN.commit()

# temp_sql()
