#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
KillerClockTimeSeidor main application
"""

import sys
import uuid
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QSpinBox, QDateTimeEdit
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

class Task:
    def __init__(self, description, start_time, end_time, hours, minutes, seconds, executions):
        self.id = str(uuid.uuid4())
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.executions = executions
        self.executed_times = 0

class TaskConfigWindow(QWidget):
    def __init__(self, daemon):
        super().__init__()
        self.daemon = daemon
        self.init_ui()
        # No destruir la ventana al cerrarla
        self.setAttribute(Qt.WA_DeleteOnClose, False)

    def closeEvent(self, event):
        # Ocultar en lugar de cerrar
        event.ignore()
        self.hide()

    def init_ui(self):
        layout = QVBoxLayout()

        # Descripción
        self.description = QLineEdit()
        layout.addWidget(QLabel("Descripción:"))
        layout.addWidget(self.description)

        # Fecha y hora de inicio
        self.start_time = QDateTimeEdit()
        self.start_time.setDateTime(datetime.now())
        layout.addWidget(QLabel("Fecha y hora de inicio:"))
        layout.addWidget(self.start_time)

        # Fecha y hora de fin
        self.end_time = QDateTimeEdit()
        self.end_time.setDateTime(datetime.now())
        layout.addWidget(QLabel("Fecha y hora de fin:"))
        layout.addWidget(self.end_time)

        # Cadencia
        layout.addWidget(QLabel("Cadencia:"))
        self.hours = QSpinBox()
        self.hours.setMaximum(23)
        layout.addWidget(QLabel("Horas:"))
        layout.addWidget(self.hours)

        self.minutes = QSpinBox()
        self.minutes.setMaximum(59)
        layout.addWidget(QLabel("Minutos:"))
        layout.addWidget(self.minutes)

        self.seconds = QSpinBox()
        self.seconds.setMaximum(59)
        layout.addWidget(QLabel("Segundos:"))
        layout.addWidget(self.seconds)

        # Número de ejecuciones
        self.executions = QSpinBox()
        self.executions.setMinimum(1)
        self.executions.setMaximum(999999)
        layout.addWidget(QLabel("Número de ejecuciones:"))
        layout.addWidget(self.executions)

        # Botón de guardar
        save_button = QPushButton("Guardar tarea")
        save_button.clicked.connect(self.save_task)
        layout.addWidget(save_button)

        self.setLayout(layout)
        self.setWindowTitle("Configurar nueva tarea")
        self.setGeometry(300, 300, 400, 500)

    def save_task(self):
        task = Task(
            self.description.text(),
            self.start_time.dateTime().toPython(),
            self.end_time.dateTime().toPython(),
            self.hours.value(),
            self.minutes.value(),
            self.seconds.value(),
            self.executions.value()
        )
        self.daemon.add_task(task)
        self.close()

class TaskListWindow(QWidget):
    def __init__(self, daemon):
        super().__init__()
        self.daemon = daemon
        self.init_ui()
        # No destruir la ventana al cerrarla
        self.setAttribute(Qt.WA_DeleteOnClose, False)

    def closeEvent(self, event):
        # Detener el timer cuando se cierra la ventana
        self.timer.stop()
        # Ocultar en lugar de cerrar
        event.ignore()
        self.hide()

    def showEvent(self, event):
        # Reiniciar el timer cuando se muestra la ventana
        self.timer.start()
        super().showEvent(event)

    def update_time(self):
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.time_label.setText(current_time)

    def init_ui(self):
        self.setWindowTitle('Tareas Programadas')
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Reloj del sistema
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        font = self.time_label.font()
        font.setPointSize(12)  # Tamaño de fuente más grande
        font.setBold(True)     # Texto en negrita
        self.time_label.setFont(font)
        self.update_time()     # Actualizar la hora inicial
        layout.addWidget(self.time_label)

        # Timer para actualizar el reloj cada segundo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Actualizar cada 1000ms (1 segundo)

        # Botón de nueva tarea
        new_task_button = QPushButton('Nueva Tarea')
        new_task_button.clicked.connect(self.daemon.show_config_window)
        layout.addWidget(new_task_button)

        # Lista de tareas con selección
        from PySide6.QtWidgets import QListWidget, QHBoxLayout
        self.task_list_widget = QListWidget()
        layout.addWidget(self.task_list_widget)

        # Botones de acción
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton('Actualizar')
        refresh_button.clicked.connect(self.update_task_list)
        button_layout.addWidget(refresh_button)

        delete_button = QPushButton('Eliminar Tarea')
        delete_button.clicked.connect(self.delete_selected_task)
        button_layout.addWidget(delete_button)

        layout.addLayout(button_layout)
        
        # Configurar tamaño de la ventana
        self.setGeometry(300, 300, 500, 400)

    def update_task_list(self):
        self.task_list_widget.clear()
        # Crear una copia de las keys para poder modificar el diccionario durante la iteración
        task_ids = list(self.daemon.tasks.keys())
        
        for task_id in task_ids:
            task = self.daemon.tasks.get(task_id)
            if not task:
                continue
                
            job = self.daemon.scheduler.get_job(task_id)
            if not job:
                # La tarea ya no está en el scheduler, ha sido completada
                task_text = f'[Completada] {task.description}\n'
                task_text += f'Ejecuciones realizadas: {task.executed_times}'
                # Eliminar la tarea completada del diccionario
                del self.daemon.tasks[task_id]
            else:
                # Formatear la fecha de próxima ejecución
                next_run = job.next_run_time.strftime('%d/%m/%Y %H:%M:%S')
                task_text = f'[Activa] {task.description}\n'
                task_text += f'Próxima ejecución: {next_run}\n'
                task_text += f'Ejecuciones: {task.executed_times}/{task.executions if task.executions > 0 else "infinitas"}'
            
            # Agregar el ID de la tarea como dato del item
            from PySide6.QtWidgets import QListWidgetItem
            item = QListWidgetItem(task_text)
            item.setData(Qt.UserRole, task_id)
            self.task_list_widget.addItem(item)

    def delete_selected_task(self):
        current_item = self.task_list_widget.currentItem()
        if not current_item:
            return

        task_id = current_item.data(Qt.UserRole)
        if task_id in self.daemon.tasks:
            # Eliminar la tarea del scheduler y del diccionario
            self.daemon.scheduler.remove_job(task_id)
            del self.daemon.tasks[task_id]
            # Actualizar la lista
            self.update_task_list()

class TaskDaemon:
    def __init__(self, app):
        self.app = app
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.tasks = {}
        self.config_window = None
        self.task_list_window = None
        self.setup_tray()

    def setup_tray(self):
        # Crear el icono del system tray
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setPen(QColor(0, 0, 0))
        painter.setBrush(QColor(0, 255, 0))
        painter.drawEllipse(0, 0, 32, 32)
        painter.end()

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(pixmap))
        self.tray.setVisible(True)

        # Crear el menú del system tray
        menu = QMenu()
        show_config_action = menu.addAction("Nueva tarea")
        show_config_action.triggered.connect(self.show_config_window)
        show_list_action = menu.addAction("Ver tareas")
        show_list_action.triggered.connect(self.show_task_list)
        quit_action = menu.addAction("Salir")
        quit_action.triggered.connect(self.quit_application)

        self.tray.setContextMenu(menu)

    def show_config_window(self):
        if not self.config_window:
            self.config_window = TaskConfigWindow(self)
        self.config_window.show()

    def show_task_list(self):
        if not self.task_list_window:
            self.task_list_window = TaskListWindow(self)
        self.task_list_window.show()
        self.task_list_window.update_task_list()

    def add_task(self, task):
        self.tasks[task.id] = task
        
        # Calcular el intervalo en segundos
        interval = task.hours * 3600 + task.minutes * 60 + task.seconds
        if interval == 0:
            # Si el intervalo es 0, establecer un valor mínimo de 1 segundo
            interval = 1

        def task_execution():
            task = self.tasks.get(task.id)
            if not task:
                return

            # Verificar si se ha alcanzado la fecha de fin
            end_time = task.end_time
            if datetime.now() >= end_time:
                self.scheduler.remove_job(task.id)
                self.show_popup(f"Tarea finalizada: {task.description}\nMotivo: Se alcanzó la fecha de fin ({end_time})")
                return
            
            if task.executed_times >= task.executions and task.executions > 0:
                self.scheduler.remove_job(task.id)
                self.show_popup(f"Tarea finalizada: {task.description}\nMotivo: Se completaron todas las ejecuciones ({task.executions})")
                return
            
            task.executed_times += 1
            self.show_popup(f"Tarea: {task.description}\nEjecución {task.executed_times} de {task.executions if task.executions > 0 else 'infinitas'}")
            
            # Si hay una ventana de lista de tareas abierta, actualizarla
            if self.task_list_window and self.task_list_window.isVisible():
                self.task_list_window.update_task_list()

        # Verificar si la hora de inicio ya pasó
        now = datetime.now()
        next_run = task.start_time
        
        # Si la hora de inicio ya pasó, calcular la próxima ejecución
        if now > task.start_time:
            # Calcular cuántas ejecuciones se han perdido
            time_diff = (now - task.start_time).total_seconds()
            intervals_passed = int(time_diff / interval)
            next_run = task.start_time + timedelta(seconds=(intervals_passed + 1) * interval)
            
            # Si la próxima ejecución es después de la hora de fin, no agregar la tarea
            if next_run >= task.end_time:
                return
        
        self.scheduler.add_job(
            task_execution,
            trigger=IntervalTrigger(seconds=interval),
            id=task.id,
            next_run_time=next_run,
            misfire_grace_time=interval  # Permitir un retraso máximo de un intervalo
        )

    def show_popup(self, message):
        self.tray.showMessage("Ejecución de tarea", message, QSystemTrayIcon.MessageIcon.Information)

    def quit_application(self):
        self.scheduler.shutdown()
        self.app.quit()

    def run(self):
        # Ya no necesitamos este método ya que la aplicación se ejecuta desde el main


if __name__ == "__main__":
    # Crear la aplicación antes del daemon para mantenerla viva
    app = QApplication(sys.argv)
    daemon = TaskDaemon(app)
    # Ejecutar el bucle principal de la aplicación
    sys.exit(app.exec())