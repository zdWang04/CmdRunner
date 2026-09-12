from dataclasses import dataclass
from multiprocessing import cpu_count


@dataclass
class Config:
    dry_run: bool = False
    _max_worker: int = 20

    # # temp_path
    # @property
    # def temp_path(self) -> Path:
    #     return self._temp_path

    # @temp_path.setter
    # def temp_path(self, value: str | Path):
    #     self._temp_path = to_path(value)

    # # log_path
    # @property
    # def log_path(self) -> Path:
    #     return self._log_path

    # @log_path.setter
    # def log_path(self, value: Path | str):
    #     self._log_path = to_path(value)

    @property
    def max_worker(self) -> int:
        return self._max_worker

    @max_worker.setter
    def max_worker(self, value: int):
        cpu_cnt = cpu_count()
        self._max_worker = max(1, min(cpu_cnt - 2 if cpu_cnt > 2 else cpu_cnt, value))

    def __post_init__(self):
        self.max_worker = self._max_worker


GLOBAL_CONFIG = Config()
