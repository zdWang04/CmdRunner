from ._state import config
from .task import (
    create_parallel_tasks_from_list,
    create_serial_tasks_from_list,
    create_single_task,
    create_tasks_from_task,
)

__all__ = [
    "config",
    "create_parallel_tasks_from_list",
    "create_serial_tasks_from_list",
    "create_single_task",
    "create_tasks_from_task",
]
