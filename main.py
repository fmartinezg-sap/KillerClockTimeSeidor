#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
KillerClockTimeSeidor main application
"""

import sys
import uuid
import sqlite3
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QSpinBox, QDateTimeEdit
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class Task:
    def __init__(self, description, start_time, end_time, hours, minutes, seconds, executions, task_id=None, executed_times=0):
        self.id = task_id or str(uuid.uuid4())
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.executions = executions
        self.executed_times = executed_times

class TaskDatabase:
    def __init__(self):
        self.conn = sqlite3.connect('tasks.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
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
        self.conn.commit()

    def save_task(self, task):
        cursor = self.conn.cursor()
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
        self.conn.commit()

    def load_tasks(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tasks")
        tasks = []
        for row in cursor.fetchall():
            tasks.append(Task(
                task_id=row[0],
                description=row[1],
                start_time=datetime.fromisoformat(row[2]),
                end_time=datetime.fromisoformat(row[3]),
                hours=row[4],
                minutes=row[5],
                seconds=row[6],
                executions=row[7],
                executed_times=row[8]
            ))
        return tasks

    def update_task_executed_times(self, task_id, executed_times):
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE tasks
        SET executed_times = ?
        WHERE id = ?
        """, (executed_times, task_id))
        self.conn.commit()

    def delete_task(self, task_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

[RESTO_DEL_CÓDIGO_ORIGINAL_HASTA_TASKDAEMON]

class TaskDaemon:
    def __init__(self, app):
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.tasks = {}
        self.config_window = None
        self.task_list_window = None
        self.db = TaskDatabase()
        self.setup_tray()
        self.load_saved_tasks()

    def load_saved_tasks(self):
        saved_tasks = self.db.load_tasks()
        for task in saved_tasks:
            self.tasks[task.id] = task
            self.schedule_task(task)

    def schedule_task(self, task):
        interval = task.hours * 3600 + task.minutes * 60 + task.seconds
        if interval == 0:
            interval = 1

        def task_execution():
            task = self.tasks.get(task.id)
            if not task:
                return

            # Verificar si se ha alcanzado la fecha de fin
            end_time = task.end_time
            if datetime.now() >= end_time:
                self.scheduler.remove_job(task.id)
                self.db.delete_task(task.id)
                self.show_popup(f"Tarea finalizada: {task.description}\nMotivo: Se alcanzó la fecha de fin ({end_time})")
                return
            
            if task.executed_times >= task.executions and task.executions > 0:
                self.scheduler.remove_job(task.id)
                self.db.delete_task(task.id)
                self.show_popup(f"Tarea finalizada: {task.description}\nMotivo: Se completaron todas las ejecuciones ({task.executions})")
                return
            
            task.executed_times += 1
            self.db.update_task_executed_times(task.id, task.executed_times)
            self.show_popup(f"Tarea: {task.description}\nEjecución {task.executed_times} de {task.executions if task.executions > 0 else 'infinitas'}")
            
            # Si hay una ventana de lista de tareas abierta, actualizarla
            if self.task_list_window and self.task_list_window.isVisible():
                self.task_list_window.update_task_list()

        # Verificar si la hora de inicio ya pasó
        now = datetime.now()
        next_run = task.start_time
        
        # Si la hora de inicio ya pasó, calcular la próxima ejecución
        if now > task.start_time:
            time_diff = (now - task.start_time).total_seconds()
            intervals_passed = int(time_diff / interval)
            next_run = task.start_time + timedelta(seconds=(intervals_passed + 1) * interval)
            
            if next_run >= task.end_time:
                return
        
        self.scheduler.add_job(
            task_execution,
            trigger=IntervalTrigger(seconds=interval),
            id=task.id,
            next_run_time=next_run,
            misfire_grace_time=interval
        )

    def add_task(self, task):
        self.tasks[task.id] = task
        self.db.save_task(task)
        self.schedule_task(task)

    def quit_application(self):
        self.scheduler.shutdown()
        self.db.close()
        self.app.quit()

[RESTO_DEL_CÓDIGO_ORIGINAL]