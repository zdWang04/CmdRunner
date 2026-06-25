from pathlib import Path
import shutil


def to_path(path: str | Path) -> Path:
    return Path(path).resolve() if isinstance(path, str) else path.resolve()


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
    if folder.exists():
        shutil.rmtree(folder, ignore_errors=False)
