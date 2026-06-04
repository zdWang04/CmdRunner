from functools import partial
from subprocess import run, CalledProcessError
from typing import Optional, List
from multiprocessing import Pool, cpu_count
import sys
from timer import Timer

from config import GLOBAL_CONFIG as cfg

__prun = partial(run, shell=True, executable="/bin/bash", check=True, text=True)


class Task:
    """
    任务类
    cmd: 需要运行的命令
    tag: 用于区分的标签
    id : 任务id
    """

    def __init__(self, cmd: str, tag: str = "", id: int = 0) -> None:
        self.cmd = cmd
        self.tag = tag
        self.id = id
        self.timer = Timer()
        self.successed = False
        self.error = None

    def __task_report(self) -> str:
        return (
            f"[SUCCESSED] | {self.timer.done()} | {self.id} | {self.tag} | {self.cmd}"
            if self.successed
            else f"[FAILED]    | {self.timer.done()} | {self.id} | {self.tag} | {self.error} | {self.cmd}"
        )

    def run(self):
        if cfg.dry_run:
            self.successed = True
            print("[DRY_RUN]")
        else:
            try:
                self.timer.reset()
                __prun(self.cmd)
                self.successed = True
            except CalledProcessError as e:
                self.error = e

        print(self.__task_report())


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

        self.max_worker: int = max(cfg.max_worker, cpu_count() - 2)

    @staticmethod
    def __wrapper(task: Task) -> None:
        task.run()

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

    def __task_report(self) -> None:

        print(f"\n{'=' * 50}")
        print(f"All task done! Time: {self.global_timer.done()}")

        self.__update_result_dict()
        print(f"|{'successed':=^50}|")
        for task in self.result["SUCCESSED"]:
            print(task.__task_report())
        print(f"|{'failed':=^50}|")
        for task in self.result["FAILED"]:
            print(task.__task_report())

    def run(self):
        if cfg.dry_run:
            for task in self.tasks:
                task.run()
            self.__task_report()
            return

        self.global_timer.reset()

        with Pool(processes=self.max_worker) as pool:
            try:
                for _ in pool.imap_unordered(self.__wrapper, self.tasks):
                    pass
            except KeyboardInterrupt:
                print("\n\n[!] Stopped by KeyboardInterrupt")
                pool.terminate()
                pool.join()
                sys.exit(1)

        self.__task_report()
