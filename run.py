from functools import partial
from subprocess import run, CalledProcessError
from typing import Optional, List
from multiprocessing import Pool
import sys
from timer import Timer

from config import GLOBAL_CONFIG as cfg
from utils import mkdir

_prun = partial(run, shell=True, executable="/bin/bash", check=True, text=True)


class Task:
    """
    任务类
    cmd: 需要运行的命令
    tag: 用于区分的标签
    id : 任务id
    """

    def __init__(self, cmd: str, tag: str = "task", id: int = 0) -> None:
        self.cmd = cmd
        self.tag = tag
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
            else f"[FAILED]    | {self.timer.done()} | {self.id} | {self.tag} | {self.error} | {self.cmd}"
        )

    def run(self):
        if cfg.dry_run:
            self.successed = True
            print("[DRY_RUN]")
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


def _tasks_run_wrapper(task: Task):
    task.run()


class Tasks:
    def __init__(
        self,
        cmds: List[str],
        tags: Optional[List[str]] = None,
    ) -> None:
        self.cmds: List[str] = cmds
        self.tags: List[str] = (
            tags if tags is not None else [f"task_{i}" for i in range(len(self.cmds))]
        )
        self.global_timer: Timer = Timer()
        self.tasks: List[Task] = self.__make_tasks()

        self.result: dict[str, List[Task]] = {"SUCCESSED": [], "FAILED": []}

    def __make_tasks(self) -> List[Task]:
        task_list = []
        for idx, cmd in enumerate(self.cmds):
            task = Task(cmd=cmd, tag=self.tags[idx], id=idx)
            task_list.append(task)
        return task_list

    def __update_result_dict(self) -> None:
        for task in self.tasks:
            if task.successed:
                self.result["SUCCESSED"].append(task)
            else:
                self.result["FAILED"].append(task)

    def _task_report(self) -> None:

        print(f"\n{'=' * 50}")
        print(f"All task done! Time: {self.global_timer.done()}")

        self.__update_result_dict()
        print(f"|{'SUCCESSED':=^50}|")
        for task in self.result["SUCCESSED"]:
            print(task._task_report())
        print(f"|{'FAILED':=^50}|")
        for task in self.result["FAILED"]:
            print(task._task_report())

    def run(self):
        if cfg.dry_run:
            for task in self.tasks:
                task.run()
            self._task_report()
            return
        if len(self.cmds) < cfg.max_worker:
            cfg.max_worker = len(self.cmds)
            print(
                f"number of cmds is less than `max_worker`, using {len(self.cmds)} workers instead"
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

        self._task_report()
