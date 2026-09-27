RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
ORANGE = "\033[38;5;208m"


def _color_print(color: str, *args, **kwargs) -> None:
    print("\n")
    print(color, end="")
    print(*args, **kwargs)
    print(RESET, end="")
    print("\n")


def print_red(*args, **kwargs) -> None:
    _color_print(RED, *args, **kwargs)


def print_green(*args, **kwargs) -> None:
    _color_print(GREEN, *args, **kwargs)


def print_orange(*args, **kwargs) -> None:
    _color_print(ORANGE, *args, **kwargs)
