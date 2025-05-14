from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton
from PySide6.QtCore import Qt

class TaskListWindow(QWidget):

    def update_time(self):
        from datetime import datetime
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.time_label.setText(current_time)

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
        self.task_list_widget = QListWidget()
        # Reloj del sistema
        from PySide6.QtCore import QTimer
        from datetime import datetime
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        font = self.time_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.time_label.setFont(font)
        self.update_time()
        layout.addWidget(self.time_label)

        # Timer para actualizar el reloj cada segundo
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        layout.addWidget(QLabel("Tareas activas:"))
        layout.addWidget(self.task_list_widget)

        # Botón para refresco manual
        refresh_button = QPushButton("Actualizar ahora")
        refresh_button.clicked.connect(self.update_task_list)
        layout.addWidget(refresh_button)

        # Timer para refresco automático
        from PySide6.QtCore import QTimer
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.update_task_list)
        self.refresh_timer.start(1000)

        # Botón para crear tarea
        create_button = QPushButton("Crear tarea")
        create_button.clicked.connect(self.daemon.show_config_window)
        layout.addWidget(create_button)

        # Botón para eliminar tarea seleccionada
        delete_button = QPushButton("Eliminar tarea seleccionada")
        delete_button.clicked.connect(self.delete_selected_task)
        layout.addWidget(delete_button)
        self.setLayout(layout)
        self.setWindowTitle("Lista de tareas")
        self.setGeometry(350, 350, 400, 400)

    def update_task_list(self):
        self.task_list_widget.clear()
        from datetime import datetime
        for task_id, task in self.daemon.tasks.items():
            # Formatear las fechas al formato DD/MM/AAAA HH:MM:SS
            start_str = task.start_time.strftime('%d/%m/%Y %H:%M:%S') if hasattr(task.start_time, 'strftime') else str(task.start_time)
            end_str = task.end_time.strftime('%d/%m/%Y %H:%M:%S') if hasattr(task.end_time, 'strftime') else str(task.end_time)
            # Obtener la próxima ejecución si existe
            next_run_str = "No programada"
            job = self.daemon.scheduler.get_job(task_id) if hasattr(self.daemon, 'scheduler') else None
            if job and hasattr(job, 'next_run_time') and job.next_run_time:
                next_run_str = job.next_run_time.strftime('%d/%m/%Y %H:%M:%S')
            # Mostrar la descripción y el resto en formato normal
            task_text = f"{task.description} ({start_str} - {end_str})\nIntervalo: {task.hours}h {task.minutes}m {task.seconds}s "
            task_text += f'\nPróxima ejecución: {next_run_str}'
            task_text += f'\nEjecuciones: {task.executed_times}/{task.executions if task.executions > 0 else "infinitas"}'
            from PySide6.QtWidgets import QListWidgetItem
            item = QListWidgetItem(task_text)
            item.setData(Qt.UserRole, task_id)
            self.task_list_widget.addItem(item)
        if self.task_list_widget.count() == 0:
            self.task_list_widget.addItem('No hay tareas programadas')

    def delete_selected_task(self):
        current_item = self.task_list_widget.currentItem()
        if not current_item:
            return
        task_id = current_item.data(Qt.UserRole)
        if not task_id:
            return
        job = self.daemon.scheduler.get_job(task_id)
        if job:
            self.daemon.scheduler.remove_job(task_id)
        if task_id in self.daemon.tasks:
            del self.daemon.tasks[task_id]
        self.daemon.db.delete_task(task_id)
        self.update_task_list()
        self.daemon.show_popup(f'Tarea eliminada')

