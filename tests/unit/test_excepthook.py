import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# 导入 PhoneMic
import phonemic.PhoneMic

def test_excepthook_writes_crash_log(monkeypatch, tmp_path):
    # 重设日志目录以避免污染用户文件
    mock_log_dir = tmp_path / ".phonemic"
    mock_crash_log = mock_log_dir / "crash.log"
    mock_log_dir.mkdir(parents=True, exist_ok=True)
    
    monkeypatch.setattr(phonemic.PhoneMic, "LOG_DIR", mock_log_dir)
    monkeypatch.setattr(phonemic.PhoneMic, "CRASH_LOG", mock_crash_log)
    
    # 模拟一个异常
    try:
        raise ValueError("Simulated startup crash")
    except ValueError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
    # 调用异常处理器，我们期望它用 SystemExit(1) 退出，并且把崩溃堆栈写入文件
    with patch("PySide6.QtWidgets.QMessageBox.critical") as mock_critical:
        with pytest.raises(SystemExit) as exc_info:
            phonemic.PhoneMic.handle_exception(exc_type, exc_value, exc_traceback)
        assert exc_info.value.code == 1
        
    # 验证日志文件的写入
    assert mock_crash_log.exists()
    content = mock_crash_log.read_text(encoding="utf-8")
    assert "Simulated startup crash" in content
    assert "ValueError" in content
