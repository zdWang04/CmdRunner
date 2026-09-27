from __future__ import annotations

import signal
from functools import partial
from subprocess import run
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .core import TaskType

_shell_run = partial(
    run,
    shell=True,
    executable="/bin/bash",
    check=True,
    text=True,
    start_new_session=True,
)


def _init_worker() -> None:
    """worker 启动时忽略 SIGINT，Ctrl+C 只由父进程处理。"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def _tasks_run_wrapper(task: TaskType):
    """
    专为 pool.imap_unordered 而用
    """
    task.run()
