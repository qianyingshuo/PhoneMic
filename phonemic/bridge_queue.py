import multiprocessing
from typing import Any
from .bridge_interface import EventBridge

class QueueEventBridge(EventBridge):
    def __init__(self, queue: multiprocessing.Queue):
        self.queue = queue

    def emit(self, event_type: str, payload: Any = None) -> None:
        self.queue.put((event_type, payload))