import unittest
from PySide6.QtCore import QCoreApplication
from phonemic.bridge_qt import QtEventBridge
import sys

class TestQtEventBridge(unittest.TestCase):
    def test_instantiation_and_emit(self):
        # A QCoreApplication instance is required for Qt's signal/slot mechanism
        app = QCoreApplication.instance()
        if app is None:
            # Create a new QCoreApplication if none exists
            # The sys.argv is passed to allow for Qt-specific command-line arguments
            app = QCoreApplication(sys.argv)

        try:
            bridge = QtEventBridge()
            # Test if emit can be called without errors
            bridge.emit("test_event", {"data": "test_data"})
        except Exception as e:
            self.fail(f"QtEventBridge failed with exception: {e}")

if __name__ == '__main__':
    unittest.main()
