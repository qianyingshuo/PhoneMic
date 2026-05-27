"""
上屏逻辑：模拟 Ctrl+V 粘贴文本，并恢复原剪贴板内容。
同时提供按键序列执行功能（支持逗号分隔多个组合）。
"""
import logging
import time
from typing import Tuple, List

import pyautogui
import pyperclip

logger = logging.getLogger(__name__)

# ---------- 剪贴板粘贴（原有功能） ----------
def flash_insert(text: str) -> None:
    """
    将文本粘贴到当前光标位置，并恢复原剪贴板内容。
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if text == "":
        logger.warning("flash_insert called with empty text, doing nothing")
        return

    original_clipboard = None
    try:
        original_clipboard = pyperclip.paste()
        logger.debug("Original clipboard content saved")

        pyperclip.copy(text)
        logger.debug(f"Text copied to clipboard: {text[:50]}...")

        pyautogui.hotkey('ctrl', 'v')
        logger.debug("Ctrl+V simulated")

    except pyperclip.PyperclipException as e:
        raise RuntimeError(f"Clipboard operation failed: {e}") from e
    except pyautogui.FailSafeException as e:
        raise RuntimeError(f"PyAutoGUI failsafe triggered: {e}") from e
    except Exception as e:
        raise RuntimeError(f"Unexpected error during flash_insert: {e}") from e
    finally:
        if original_clipboard is not None:
            try:
                pyperclip.copy(original_clipboard)
                logger.debug("Original clipboard restored")
            except pyperclip.PyperclipException as e:
                logger.critical(f"Failed to restore original clipboard: {e}")
        else:
            logger.warning("No original clipboard to restore")

# ---------- 按键序列执行（新增功能） ----------
# 可用键名集合（来自 pyautogui）
VALID_KEYS = set(pyautogui.KEYBOARD_KEYS)
MODIFIERS = {'ctrl', 'shift', 'alt', 'win'}

def _validate_single_combination(keys: str) -> Tuple[bool, str]:
    """校验单个按键组合（不含逗号），返回 (是否合法, 错误信息)"""
    if not keys or not keys.strip():
        return False, "按键字符串不能为空"
    keys_lower = keys.strip().lower()
    parts = keys_lower.split('+')
    for part in parts:
        if part not in VALID_KEYS:
            if part not in MODIFIERS or len(parts) == 1:
                return False, f"未知键名: '{part}'，请使用 pyautogui 支持的键名"
    return True, ""

def validate_key_sequence(keys_sequence: str) -> Tuple[bool, str]:
    """
    校验按键序列（支持逗号分隔多个组合）。
    返回 (是否合法, 错误信息)
    """
    if not keys_sequence or not keys_sequence.strip():
        return False, "按键序列不能为空"

    # 按逗号分割，并去除每个组合的前后空格
    combos = [c.strip() for c in keys_sequence.split(',')]
    if len(combos) > 10:
        return False, f"按键序列最多支持10个组合，当前有{len(combos)}个"

    for combo in combos:
        ok, err = _validate_single_combination(combo)
        if not ok:
            return False, f"组合 '{combo}' 无效: {err}"
    return True, ""

# 保留旧函数名作为兼容（但推荐使用 validate_key_sequence）
def validate_key_combination(keys: str) -> Tuple[bool, str]:
    """兼容旧接口：单组合校验"""
    return _validate_single_combination(keys)

def send_keys(keys_sequence: str) -> None:
    """
    模拟按键序列，支持逗号分隔多个组合。
    例如: "ctrl+a, delete" -> 先 Ctrl+A 全选，再 Delete 删除。
          "ctrl+c, enter" -> 复制后回车。
    每个组合内部使用 '+' 连接键名（如 "ctrl+shift+esc"）。
    组合之间会插入 0.05 秒的短暂延迟。
    """
    if not keys_sequence or not keys_sequence.strip():
        logger.error("按键序列为空，不做任何操作")
        return

    # 校验整个序列
    ok, err = validate_key_sequence(keys_sequence)
    if not ok:
        logger.error(f"按键序列非法: {keys_sequence} - {err}")
        return

    # 分割序列
    combos = [c.strip() for c in keys_sequence.split(',')]
    for combo in combos:
        parts = combo.lower().split('+')
        try:
            pyautogui.hotkey(*parts)
            logger.debug(f"执行组合: {combo}")
            time.sleep(0.05)  # 组合之间的短暂延迟
        except Exception as e:
            logger.exception(f"模拟按键失败，组合: {combo} - {e}")
            # 发生错误时停止后续执行，避免状态混乱
            break

# ---------- 备用粘贴方案（保留原样） ----------
import win32con
import win32gui

def flash_insert_via_paste_message(text: str):
    """使用 WM_PASTE 消息的备用粘贴方法"""
    original = pyperclip.paste()
    pyperclip.copy(text)
    try:
        hwnd = win32gui.GetForegroundWindow()
        win32gui.SendMessage(hwnd, win32con.WM_PASTE, 0, 0)
    finally:
        pyperclip.copy(original)