from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QSpinBox, QPushButton, QDateTimeEdit
from datetime import datetime
from PySide6.QtCore import Qt
from task import Task

class TaskConfigWindow(QWidget):
    def __init__(self, daemon):
        super().__init__()
        self.daemon = daemon
        self.init_ui()
        self.setAttribute(Qt.WA_DeleteOnClose, False)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def init_ui(self):
        layout = QVBoxLayout()
        self.description = QLineEdit()
        layout.addWidget(QLabel("Descripción:"))
        layout.addWidget(self.description)
        self.start_time = QDateTimeEdit()
        self.start_time.setDateTime(datetime.now())
        layout.addWidget(QLabel("Fecha y hora de inicio:"))
        layout.addWidget(self.start_time)
        self.end_time = QDateTimeEdit()
        self.end_time.setDateTime(datetime.now())
        layout.addWidget(QLabel("Fecha y hora de fin:"))
        layout.addWidget(self.end_time)
        self.hours = QSpinBox()
        self.hours.setMaximum(9999)
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
        self.executions = QSpinBox()
        self.executions.setMinimum(1)
        self.executions.setMaximum(999999)
        layout.addWidget(QLabel("Número de ejecuciones:"))
        layout.addWidget(self.executions)
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
        self.daemon.show_task_list()
        if self.daemon.task_list_window:
            self.daemon.task_list_window.update_task_list()

