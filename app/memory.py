from collections import defaultdict, deque
from threading import Lock

from .config import settings


class SessionMemory:
    def __init__(self):
        self._data = defaultdict(lambda: deque(maxlen=settings.session_history_messages))
        self._lock = Lock()

    def history(self, session_id: str) -> list[dict]:
        with self._lock:
            return list(self._data[session_id])

    def add(self, session_id: str, role: str, content: str) -> None:
        with self._lock:
            self._data[session_id].append({"role": role, "content": content})

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._data.pop(session_id, None)


memory = SessionMemory()
