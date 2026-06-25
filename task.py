import sys
from functools import partial
from subprocess import run
from typing import Optional, Union, TypeAlias
from multiprocessing import Pool
from pathlib import Path
from uuid import uuid4

from timer import Timer
from config import GLOBAL_CONFIG as cfg
from utils import mkdir

__all__ = [
    "create_single_task",
    "create_parallel_tasks_from_list",
    "create_serial_tasks_from_list",
]

_prun = partial(run, shell=True, executable="/bin/bash", check=True, text=True)

TaskType: TypeAlias = Union["_Task", "_ParallelTasks", "_SerialTasks"]


class _Task:
    """
    任务类
    cmd: 需要运行的命令
    tag: 用于区分的标签
    id : 任务id
    """

    def __init__(
        self,
        cmd: str,
        tag: str = "task",
        log_path: Path = Path("./"),
    ) -> None:
        self.cmd = cmd
        self.tag = tag
        self.id = str(uuid4())
        self.timer = Timer()

        if not cfg.dry_run:
            mkdir(log_path)
            if log_path:
                mkdir(log_path)
            self.log_stdout_file = log_path / f"{tag}_{id}.stdout.log"
            self.log_stderr_file = log_path / f"{tag}_{id}.stderr.log"

        self.successed = False
        self.error = None

    def _task_report(self) -> str:
        return (
            f"[SUCCESSED] | {self.timer.done()} | {self.id} | {self.tag} | {self.error} | {self.cmd}"
            if self.successed
            else f"[FAILED] | {self.timer.done()} | {self.id} | {self.tag} | {self.error} | {self.cmd}"
        )

    def __repr__(self) -> str:
        log_status = "ready" if hasattr(self, "log_stdout_file") else "dry_run"
        return (
            f"{self.__class__.__name__}\n"
            f"id={self.id}\n"
            f"tag={self.tag!r}\n"
            f"cmd={self.cmd[:50] + '...' if len(self.cmd) > 50 else self.cmd!r}\n"
            f"status={log_status}\n"
        )

    def run(self):
        if cfg.dry_run:
            self.successed = True
        else:
            try:
                print(f"Task Start: {self.tag}_{self.id}")
                self.timer.reset()
                with (
                    open(self.log_stdout_file, "w") as log_f,
                    open(self.log_stderr_file, "w") as error_f,
                ):
                    _prun(self.cmd, stdout=log_f, stderr=error_f)
                print(f"Task Done: {self.tag}_{self.id}")
                self.successed = True
            except Exception as e:
                self.error = e
                self.successed = False

        print(self._task_report())


def _tasks_run_wrapper(task: TaskType):
    task.run()  # if process quits correctly, `task.successed` will be set to `True`


class _ParallelTasks:
    """
    可并行运行任务类

    用于管理可并行执行的任务集合（如并行处理多个独立的 fq.gz 质控任务）。

    警告：
        传入的任务列表必须满足逻辑上的可并行性（无顺序依赖）。若传入需要严格串行执行的任务，
        将导致业务逻辑错误或未定义行为。


    Attributes:
        tasks: 任务列表
        global_timer: 全局计时器

    Methods:
        run(): 启动任务执行
    """

    def __init__(
        self,
        tasks: list[TaskType],
    ) -> None:
        self.tasks = tasks

    def __repr__(self) -> str:
        task_count = len(self.tasks)
        tasks_repr = "\n".join(repr(task) for task in self.tasks)
        return f"{self.__class__.__name__} | count={task_count} |\n{tasks_repr}"

    def run(self):
        if cfg.dry_run:
            for task in self.tasks:
                task.run()
            return
        max_worker = cfg.max_worker
        if len(self.tasks) < cfg.max_worker:
            max_worker = len(self.tasks)
            print(
                f"number of tasks is less than `max_worker`, using {len(self.tasks)} workers instead"
            )

        print(f"use {max_worker} workers")
        with Pool(processes=max_worker) as pool:
            try:
                for _ in pool.imap_unordered(_tasks_run_wrapper, self.tasks):
                    pass
            except KeyboardInterrupt:
                print("\n\n[!] Stopped by KeyboardInterrupt")
                pool.terminate()
                pool.join()
                sys.exit(1)


class _SerialTasks:
    """
    串行执行任务类

    按顺序逐个执行任务列表中的所有任务。适用于有顺序依赖或资源冲突的场景。


    Attributes:
        tasks: 任务列表
        global_timer: 全局计时器

    Methods:
        run(): 启动串行任务执行
    """

    def __init__(self, tasks: list[TaskType]) -> None:
        self.tasks = tasks

    def __repr__(self) -> str:
        task_count = len(self.tasks)
        tasks_repr = "\n".join(repr(task) for task in self.tasks)
        return f"{self.__class__.__name__} | count={task_count} |\n{tasks_repr}"

    def run(self):
        if cfg.dry_run:
            for task in self.tasks:
                task.run()
            return

        for task in self.tasks:
            try:
                task.run()
            except KeyboardInterrupt:
                print("\n\n[!] Stopped by KeyboardInterrupt")
                sys.exit(1)


def create_single_task(cmd: str, tag: Optional[str] = None) -> _Task:
    tag = tag if tag is not None else f"task_id_{id}"
    return _Task(cmd, tag)


def create_parallel_tasks_from_list(
    cmd_list: list[str], tag_list: Optional[list[str]] = None
) -> _ParallelTasks:
    tag_list = (
        tag_list if tag_list is not None else [f"cmd_{i}" for i in range(len(cmd_list))]
    )
    assert len(cmd_list) == len(tag_list), (
        "length of `cmd_list` must equal to `tag_list`"
    )
    ptasks = []
    for idx, cmd in enumerate(cmd_list):
        task = create_single_task(cmd, tag_list[idx])
        ptasks.append(task)
    ptasks = _ParallelTasks(ptasks)
    return ptasks


def create_serial_tasks_from_list(
    cmd_list: list[str], tag_list: Optional[list[str]] = None
) -> _SerialTasks:

    tag_list = (
        tag_list if tag_list is not None else [f"cmd_{i}" for i in range(len(cmd_list))]
    )

    assert len(cmd_list) == len(tag_list), (
        "length of `cmd_list` must equal to `tag_list`"
    )
    stasks = []
    for idx, cmd in enumerate(cmd_list):
        task = create_single_task(cmd, tag_list[idx])
        stasks.append(task)
    stasks = _SerialTasks(stasks)
    return stasks


def create_tasks_from_task(
    tasks: list[TaskType], parallel: bool = False
) -> _ParallelTasks | _SerialTasks:
    if parallel:
        return _ParallelTasks(tasks)
    else:
        return _SerialTasks(tasks)
