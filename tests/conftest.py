import sys
from unittest.mock import MagicMock

# Prevents Tkinter check crash on Linux Headless during pyautogui/mouseinfo import
mock_mouseinfo = MagicMock()
sys.modules['mouseinfo'] = mock_mouseinfo

# Mock pyautogui
class MockPyAutoGUI:
    KEYBOARD_KEYS = [
        'backspace', 'tab', 'enter', 'shift', 'ctrl', 'alt', 'pause', 'capslock', 'esc', 'space', 'pageup', 'pagedown',
        'end', 'home', 'left', 'up', 'right', 'down', 'select', 'print', 'execute', 'prtscr', 'prntscr', 'printscreen',
        'insert', 'delete', 'help', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
        'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'win', 'winleft',
        'winright', 'apps', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7', 'num8', 'num9', 'multiply',
        'add', 'separator', 'subtract', 'decimal', 'divide', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10',
        'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23', 'f24', 'numlock',
        'scrolllock', 'shiftleft', 'shiftright', 'ctrlleft', 'ctrlright', 'altleft', 'altright'
    ]
    FailSafeException = Exception
    
    def hotkey(self, *args, **kwargs):
        pass

mock_pyautogui = MockPyAutoGUI()
sys.modules['pyautogui'] = mock_pyautogui

# Mock win32 dependencies for linux environment
sys.modules['win32gui'] = MagicMock()
sys.modules['win32con'] = MagicMock()
