from dataclasses import dataclass


@dataclass
class Config:
    dry_run: bool = False
    max_worker = 8


GLOBAL_CONFIG = Config()
