from pathlib import Path
from typing import List


def __to_path(path: str | Path) -> Path:
    return Path(path).resolve() if isinstance(path, str) else path.resolve()


def ls(path: str | Path) -> List[Path]:
    path = __to_path(path)
    return [i.resolve() for i in path.iterdir()]


def mkdir(path: str | Path) -> Path:
    path = __to_path(path)
    path.mkdir(exist_ok=True, parents=True)
    return path.resolve()


def glob(path: str | Path, pattern: str) -> List[Path]:
    return list(__to_path(path).glob(pattern))
