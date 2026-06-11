import sys
from functools import partial
from subprocess import run, CalledProcessError
from typing import Optional
from multiprocessing import Pool

from timer import Timer
from config import GLOBAL_CONFIG as cfg
from utils import mkdir

__all__ = [
    "create_single_task",
    "create_parallel_tasks_from_list",
    "create_serial_tasks_from_list",
]

_prun = partial(run, shell=True, executable="/bin/bash", check=True, text=True)


class _Task:
    """
    任务类
    cmd: 需要运行的命令
    tag: 用于区分的标签
    id : 任务id
    """

    def __init__(self, cmd: str, tag: str = "task", id: int = 0) -> None:
        self.cmd = cmd
        self.tag = tag
        # todo: maybe use uuid.uuid4 ? how to trace cmd sequence?
        self.id = id
        self.timer = Timer()

        if not cfg.dry_run:
            mkdir(cfg.log_path)
            self.log_file = cfg.log_path / f"{tag}_{id}.log"
            self.log_error_file = cfg.log_path / f"{tag}_{id}.error.log"

        self.successed = False
        self.error = None

    def _task_report(self) -> str:
        return (
            f"[SUCCESSED] | {self.timer.done()} | {self.id} | {self.tag} | {self.error} | {self.cmd}"
            if self.successed
            else f"[FAILED] | {self.timer.done()} | {self.id} | {self.tag} | {self.error} | {self.cmd}"
        )

    def run(self):
        if cfg.dry_run:
            self.successed = True
        else:
            try:
                print(f"Task Start: {self.tag}_{self.id}")
                self.timer.reset()
                with (
                    open(self.log_file, "w") as log_f,
                    open(self.log_error_file, "w") as error_f,
                ):
                    _prun(self.cmd, stdout=log_f, stderr=error_f)
                self.successed = True
                print(f"Task Done: {self.tag}_{self.id}")
            except CalledProcessError as e:
                self.error = e

        print(self._task_report())


def _tasks_run_wrapper(task: _Task):
    task.run()  # if quit correctly, the `task.successed` will be set to `True`


def _tasks_report(global_timer: Timer, tasks: list[_Task]) -> None:

    print(f"\n{'=' * 50}")
    print(f"All task done! Global Time: {global_timer.done()}")
    result = {"SUCCESSED": [], "FAILED": []}

    for task in tasks:
        if task.successed:
            result["SUCCESSED"].append(task)
        else:
            result["FAILED"].append(task)

    print(f"|{'SUCCESSED':=^50}|")
    for task in result["SUCCESSED"]:
        print(task._task_report())
    print(f"|{'FAILED':=^50}|")
    for task in result["FAILED"]:
        print(task._task_report())


class _ParallelTasks:
    """
    可并行运行任务类

    用于管理可并行执行的任务集合（如并行处理多个独立的 fq.gz 质控任务）。

    警告：
        传入的任务列表必须满足逻辑上的可并行性（无顺序依赖）。若传入需要严格串行执行的任务，
        将导致业务逻辑错误或未定义行为。

    特性：
        - 支持进程池并行执行，自动调整 worker 数量
        - 支持 dry_run 调试模式（顺序执行）
        - 内置计时与任务报告

    Attributes:
        tasks: 任务列表
        global_timer: 全局计时器

    Methods:
        run(): 启动任务执行
    """

    def __init__(
        self,
        tasks: list[_Task],
    ) -> None:
        self.tasks = tasks
        self.global_timer: Timer = Timer()

    def run(self):
        if cfg.dry_run:
            for task in self.tasks:
                task.run()
            return
        if len(self.tasks) < cfg.max_worker:
            cfg.max_worker = len(self.tasks)
            print(
                f"number of tasks is less than `max_worker`, using {len(self.tasks)} workers instead"
            )
        print(f"use {cfg.max_worker} workers")
        self.global_timer.reset()
        with Pool(processes=cfg.max_worker) as pool:
            try:
                for _ in pool.imap_unordered(_tasks_run_wrapper, self.tasks):
                    pass
            except KeyboardInterrupt:
                print("\n\n[!] Stopped by KeyboardInterrupt")
                pool.terminate()
                pool.join()
                sys.exit(1)

        _tasks_report(self.global_timer, self.tasks)


class _SerialTasks:
    """
    串行执行任务类

    按顺序逐个执行任务列表中的所有任务。适用于有顺序依赖或资源冲突的场景。

    特性：
        - 严格按列表顺序执行
        - 支持 dry_run 调试模式
        - 内置计时与任务报告

    Attributes:
        tasks: 任务列表
        global_timer: 全局计时器

    Methods:
        run(): 启动串行任务执行
    """

    def __init__(
        self,
        tasks: list[_Task],
    ) -> None:
        self.tasks = tasks
        self.global_timer: Timer = Timer()

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

        _tasks_report(self.global_timer, self.tasks)


def create_single_task(cmd: str, tag: Optional[str] = None, id: int = 0) -> _Task:
    tag = f"some_task_{id}" if tag is None else tag
    task = _Task(cmd, tag, id)
    return task


def create_parallel_tasks_from_list(
    cmd_list: list[str], tag_list: list[Optional[str]] = [None]
) -> _ParallelTasks:
    assert len(cmd_list) == len(tag_list), (
        "length of `cmd_list` must equal to `tag_list`"
    )
    ptasks = []
    for idx, cmd in enumerate(cmd_list):
        task = create_single_task(cmd, tag_list[idx], idx)
        ptasks.append(task)
    ptasks = _ParallelTasks(ptasks)
    return ptasks


def create_serial_tasks_from_list(
    cmd_list: list[str], tag_list: list[Optional[str]] = [None]
) -> _SerialTasks:
    assert len(cmd_list) == len(tag_list), (
        "length of `cmd_list` must equal to `tag_list`"
    )
    stasks = []
    for idx, cmd in enumerate(cmd_list):
        task = create_single_task(cmd, tag_list[idx], idx)
        stasks.append(task)
    stasks = _SerialTasks(stasks)
    return stasks
