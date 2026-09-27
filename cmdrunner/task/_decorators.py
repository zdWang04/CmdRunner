import os
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from multiprocessing.pool import Pool as PoolType

from .._state import config as cfg


@contextmanager
def _handle_interrupt(pool: PoolType | None = None):
    """
    相当于上下文管理器的语法糖
    Ctrl+C 时打断，杀光所有进程
    """
    try:
        yield
    except KeyboardInterrupt:
        print("\n\n[!] Stopped by KeyboardInterrupt")

        if pool is not None:
            pool.terminate()

        os._exit(1)


def _dry_run_wrapperr(method: Callable) -> Callable:
    """
    干运行包装器
        如果 cfg.dry_run 为 True，串行遍历所有任务，只做展示，留与用户确认
        如果 cfg.dry_run 为 False，按照任务类型执行各自的 run 方法
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if cfg.dry_run:
            for task in self.tasks:
                task.run()
            return
        return method(self, *args, **kwargs)

    return wrapper
