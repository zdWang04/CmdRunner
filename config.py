from dataclasses import dataclass
from pathlib import Path
from multiprocessing import cpu_count
from utils import mkdir


@dataclass
class Config:
    _log_path: Path = Path("./zzz_log")
    _dry_run: bool = False
    _max_worker: int = 8

    @property
    def log_path(self) -> Path:
        return self._log_path

    @log_path.setter
    def log_path(self, value: Path | str):
        if isinstance(value, str):
            value = Path(value)
        self._log_path = value

    @property
    def dry_run(self) -> bool:
        return self._dry_run

    @dry_run.setter
    def dry_run(self, value: bool):
        self._dry_run = value

    @property
    def max_worker(self) -> int:
        return self._max_worker

    @max_worker.setter
    def max_worker(self, value: int):
        cpu_cnt = cpu_count()
        self._max_worker = max(1, min(cpu_cnt - 2 if cpu_cnt > 2 else cpu_cnt, value))

    def __post_init__(self):
        self.log_path = self._log_path
        mkdir(self.log_path)
        self.max_worker = self._max_worker


GLOBAL_CONFIG = Config()
