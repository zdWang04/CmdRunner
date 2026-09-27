from dataclasses import dataclass
from multiprocessing import cpu_count
from pathlib import Path

from .utils.path_utils import to_path


@dataclass
class Config:
    dry_run: bool = False
    _max_worker: int = 20
    _log_path: Path = Path("./")

    @property
    def max_worker(self) -> int:
        return self._max_worker

    @max_worker.setter
    def max_worker(self, value: int):
        cpu_cnt = cpu_count()
        self._max_worker = max(1, min(cpu_cnt - 2 if cpu_cnt > 2 else cpu_cnt, value))

    @property
    def log_path(self) -> Path:
        return self._log_path

    @log_path.setter
    def log_path(self, value: Path | str):
        self._log_path = to_path(value)
