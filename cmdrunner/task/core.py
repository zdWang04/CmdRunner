import sys
from multiprocessing import Pool
from subprocess import CalledProcessError
from uuid import uuid4

from .._state import config as cfg
from ..utils.color_utils import print_green, print_orange, print_red
from ..utils.path_utils import mkdir
from ..utils.time_utils import format_duration, get_time
from ._decorators import _dry_run_wrapperr, _handle_interrupt
from ._exec import _init_worker, _shell_run, _tasks_run_wrapper

type TaskType = _Task | _ParallelTasks | _SerialTasks


class _Task:
    """
    任务类
    cmd: 需要运行的命令
    tag: 用于区分的标签
    """

    def __init__(
        self,
        cmd: str,
        tag: str = "some_task",
    ) -> None:
        self.cmd = cmd
        self.tag = tag
        self.id = str(uuid4())
        self.err = None
        self.start = None

        self.successed = False
        # self.task_state = TaskStateReport(self.id, self.cmd, self.tag)

    def _init_logger(self):
        if not cfg.dry_run:
            mkdir(cfg.log_path)
            self.log_stdout_file = cfg.log_path / f"{self.tag}_{self.id}.stdout.log"
            self.log_stderr_file = cfg.log_path / f"{self.tag}_{self.id}.stderr.log"

    def _when_start(self):
        self._init_logger()
        start_str, self.start = get_time()
        print_orange(
            f"[RUNNING] | {self.tag} | {self.id} | {self.cmd if len(self.cmd) < 50 else self.cmd[:49]}... | {start_str} |"
        )

    def _when_done(self):
        _, end = get_time()
        duration = end - self.start  # pyright: ignore[reportOperatorIssue]
        if self.err is None:
            print_green(
                f"[SUCCESSED] | {self.tag} | {self.id} | {format_duration(duration.total_seconds())}"
            )
        else:
            print_red(
                f"[FAILED] | {self.tag} | {self.id} | {format_duration(duration.total_seconds())}"
            )

    def run(self):
        if cfg.dry_run:
            pass
        else:
            try:
                self._when_start()

                with (
                    open(self.log_stdout_file, "w") as log_f,
                    open(self.log_stderr_file, "w") as error_f,
                ):
                    _shell_run(self.cmd, stdout=log_f, stderr=error_f)

            except CalledProcessError as e:
                self.err = str(e)

        self._when_done()


class _ParallelTasks:
    """
    可并行运行任务类

    用于管理可并行执行的任务集合（如并行处理多个独立的 fq.gz 质控任务）

    警告：
        传入的任务列表必须满足逻辑上的可并行性（无顺序依赖），若传入需要严格串行执行的任务，将导致业务逻辑错误或未定义行为

    Attributes:
        tasks: 任务列表

    Methods:
        run(): 启动任务执行
    """

    def __init__(
        self,
        tasks: list[TaskType],
    ) -> None:
        self.tasks = tasks

    @_dry_run_wrapperr
    def run(self):

        max_worker = cfg.max_worker
        if len(self.tasks) < cfg.max_worker:
            max_worker = len(self.tasks)
            print(
                f"number of tasks is less than `max_worker`, using {len(self.tasks)} workers instead"
            )

        print(f"use {max_worker} workers")
        with (
            Pool(processes=max_worker, initializer=_init_worker) as pool,
            _handle_interrupt(pool),
        ):
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

    Methods:
        run(): 启动串行任务执行
    """

    def __init__(self, tasks: list[TaskType]) -> None:
        self.tasks = tasks

    @_dry_run_wrapperr
    def run(self):
        with _handle_interrupt():
            for task in self.tasks:
                task.run()
