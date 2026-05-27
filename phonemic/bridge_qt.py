from typing import Any
from PySide6.QtCore import QObject, Signal
from .bridge_interface import EventBridge

# Solution for metaclass conflict
# https://stackoverflow.com/questions/28720215/python-qt-pyside-and-abstract-base-class-metaclass-conflict
class BridgeMeta(type(QObject), type(EventBridge)):
    pass

class QtEventBridge(QObject, EventBridge, metaclass=BridgeMeta):
    event_signal = Signal(str, object)

    def emit(self, event_type: str, payload: Any = None) -> None:
        self.event_signal.emit(event_type, payload)