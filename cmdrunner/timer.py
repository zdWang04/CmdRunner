from time import time


class Timer:
    def __init__(self) -> None:
        self.start = time()

    def done(self) -> str:
        return self._render(time() - self.start)

    def _render(self, duration: float) -> str:
        if duration <= 60.0:
            return f"{duration:.2f} seconds"
        elif duration > 60.0 and duration <= 3600.0:
            return f"{duration / 60:.2f} minutes"
        else:
            return f"{duration / 3600:.2f} hours"

    def reset(self) -> None:
        self.start = time()
