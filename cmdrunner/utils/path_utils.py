import shutil
from pathlib import Path


class InvalidPathError(ValueError):
    pass


def to_path(path: str | Path) -> Path:
    if not isinstance(path, (str, Path)):
        raise TypeError(f"path must be str | Path, but got {type(path).__name__}")

    s = str(path)

    if not s or not s.strip():
        raise InvalidPathError("path is empty!")

    if "\0" in s:
        raise InvalidPathError(f"contain \\0: {path!r}")

    p = Path(path).resolve()

    return p


def ls(path: str | Path) -> list[Path]:
    path = to_path(path)
    return [i.resolve() for i in path.iterdir()]


def mkdir(path: str | Path) -> Path:
    path = to_path(path)
    path.mkdir(exist_ok=True, parents=True)
    return path.resolve()


def glob(path: str | Path, pattern: str) -> list[Path]:
    return list(to_path(path).glob(pattern))


def delete_directory(folder: Path) -> None:
    shutil.rmtree(folder, ignore_errors=False)
