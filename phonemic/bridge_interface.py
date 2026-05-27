from abc import ABC, abstractmethod
from typing import Any

class EventBridge(ABC):
    @abstractmethod
    def emit(self, event_type: str, payload: Any = None) -> None:
        """发送一个事件，线程安全。"""
        pass