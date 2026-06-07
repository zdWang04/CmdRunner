from pathlib import Path
from typing import List


def __to_path(path: str | Path) -> Path:
    return Path(path) if isinstance(path, str) else path


def ls(path: str | Path, absolute: bool = True) -> List[Path]:
    path = __to_path(path)
    return [i.resolve() if absolute else i for i in path.iterdir()]


def mkdir(path: str | Path) -> Path:
    path = __to_path(path)
    path.mkdir(exist_ok=True, parents=True)
    return path


def glob(path: str | Path, pattern: str) -> List[Path]:
    return list(__to_path(path).glob(pattern))
