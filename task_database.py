import sqlite3
from datetime import datetime
from task import Task

class TaskDatabase:
    def __init__(self):
        self.db_path = 'tasks.db'
        self.create_tables()

    def create_tables(self):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                description TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                hours INTEGER,
                minutes INTEGER,
                seconds INTEGER,
                executions INTEGER,
                executed_times INTEGER
            )
            """)
            conn.commit()

    def save_task(self, task):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO tasks (
                id, description, start_time, end_time, hours, minutes, seconds, executions, executed_times
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.id,
                task.description,
                task.start_time.isoformat(),
                task.end_time.isoformat(),
                task.hours,
                task.minutes,
                task.seconds,
                task.executions,
                task.executed_times
            ))
            conn.commit()

    def load_tasks(self):
        import sqlite3
        from datetime import datetime
        tasks = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks")
            for row in cursor.fetchall():
                tasks.append(Task(
                    description=row[1],
                    start_time=datetime.fromisoformat(row[2]),
                    end_time=datetime.fromisoformat(row[3]),
                    hours=row[4],
                    minutes=row[5],
                    seconds=row[6],
                    executions=row[7],
                    task_id=row[0],
                    executed_times=row[8]
                ))
        return tasks

    def update_task_executed_times(self, task_id, executed_times):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE tasks
            SET executed_times = ?
            WHERE id = ?
            """, (executed_times, task_id))
            conn.commit()

    def delete_task(self, task_id):
        import sqlite3
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()

    def close(self):
        pass  # Ya no es necesario cerrar la conexión, se usa with en cada método

