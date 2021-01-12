import time
import datetime

_INITIAL_TIMESTAMP = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).timestamp()


class Deadline:
    @staticmethod
    def after_seconds(seconds: float) -> "Deadline":
        return Deadline(time.time() + seconds)

    __slots__ = ("_deadline_at",)

    def __init__(self, deadline_at: float):
        if deadline_at < _INITIAL_TIMESTAMP:
            raise RuntimeError(f"Invalid deadline_at {deadline_at}: should be >= {_INITIAL_TIMESTAMP}")

        self._deadline_at = deadline_at

    @property
    def timeout(self) -> float:
        return max(self._deadline_at - time.time(), 0.001)  # 0 is infinite

    @property
    def expired(self) -> bool:
        return self._deadline_at - time.time() <= 0

    def __str__(self) -> str:
        return str(self._deadline_at)