import sys
from PySide6.QtWidgets import QApplication
from task_daemon import TaskDaemon

if __name__ == "__main__":
    app = QApplication(sys.argv)
    daemon = TaskDaemon(app)
    daemon.run()
