import sys
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import QPoint
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from task_database import TaskDatabase
from task_list_window import TaskListWindow
from task_config_window import TaskConfigWindow

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

    def setup_tray(self):
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        blade_color = QColor(192, 192, 192)
        handle_color = QColor(139, 69, 19)
        painter.setBrush(blade_color)
        painter.setPen(blade_color)
        points = [QPoint(5, 16), QPoint(20, 12), QPoint(20, 20)]
        painter.drawPolygon(points)
        painter.setBrush(handle_color)
        painter.setPen(handle_color)
        painter.drawRect(20, 13, 8, 6)
        painter.end()
        icon = QIcon(pixmap)
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(icon)
        self.tray.setVisible(True)
        menu = QMenu()
        view_tasks_action = menu.addAction("Ver tareas")
        view_tasks_action.triggered.connect(self.show_task_list)
        new_task_action = menu.addAction("Nueva tarea")
        new_task_action.triggered.connect(self.show_config_window)
        exit_action = menu.addAction("Salir")
        exit_action.triggered.connect(self.quit_application)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def show_config_window(self):
        try:
            if self.config_window is None or not self.config_window.isVisible():
                self.config_window = TaskConfigWindow(self)
            self.config_window.show()
            self.config_window.raise_()
            self.config_window.activateWindow()
        except Exception as e:
            self.show_popup(f"Error al mostrar ventana de configuración: {str(e)}")

    def show_task_list(self):
        try:
            if self.task_list_window is None or not self.task_list_window.isVisible():
                self.task_list_window = TaskListWindow(self)
            self.task_list_window.update_task_list()
            self.task_list_window.show()
            self.task_list_window.raise_()
            self.task_list_window.activateWindow()
        except Exception as e:
            self.show_popup(f"Error al mostrar lista de tareas: {str(e)}")

    def add_task(self, task):
        self.tasks[task.id] = task
        self.db.save_task(task)
        self.schedule_task(task)

    def schedule_task(self, task):
        interval = task.hours * 3600 + task.minutes * 60 + task.seconds
        if interval == 0:
            interval = 1
        def task_execution():
            now = datetime.now()
            if now >= task.end_time:
                self.scheduler.remove_job(task.id)
                self.db.delete_task(task.id)
                self.show_popup(f"Tarea finalizada: {task.description}\nMotivo: Se alcanzó la fecha de fin ({task.end_time})")
                return
            if task.executed_times >= task.executions and task.executions > 0:
                self.scheduler.remove_job(task.id)
                self.db.delete_task(task.id)
                self.show_popup(f"Tarea finalizada: {task.description}\nMotivo: Se completaron todas las ejecuciones ({task.executions})")
                return
            task.executed_times += 1
            self.db.update_task_executed_times(task.id, task.executed_times)
            self.show_popup(f"Tarea: {task.description}\nEjecución {task.executed_times} de {task.executions if task.executions > 0 else 'infinitas'}")
            if self.task_list_window:
                self.task_list_window.update_task_list()
        self.scheduler.add_job(task_execution, 'interval', seconds=interval, id=task.id, replace_existing=True)

    def show_popup(self, message):
        self.tray.showMessage("KillerClockTimeSeidor", message)

    def quit_application(self):
        self.scheduler.shutdown()
        self.db.close()
        self.app.quit()

    def run(self):
        self.app.exec()

