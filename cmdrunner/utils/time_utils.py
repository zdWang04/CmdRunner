import datetime


def get_time() -> tuple[str, datetime.datetime]:
    now = datetime.datetime.now(datetime.UTC)
    return now.strftime("%Y/%m/%d %H:%M:%S"), now


def format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "-"
    if seconds < 60:
        return f"{seconds:.2f}s"
    m, s = divmod(seconds, 60)
    if m < 60:
        return f"{int(m)}m {s:.1f}s"
    h, m = divmod(m, 60)
    return f"{int(h)}h {int(m)}m {s:.2f}s"
