import uuid
from datetime import datetime

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

