from pathlib import Path
from typing import List


def ls(path: str, absolute: bool = True) -> List[Path]:
    return [i.resolve() if absolute else i for i in Path(path).iterdir()]


def mkdir(path: str | Path) -> None:
    path = path if isinstance(path, Path) else Path(path)
    Path(path).mkdir(exist_ok=True, parents=True)


def glob(path: str, pattern: str) -> List[Path]:
    return list(Path(path).glob(pattern))
