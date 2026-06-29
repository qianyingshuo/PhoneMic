import sys
from pathlib import Path
from unittest.mock import patch
import pytest

from phonemic.utils.paths import get_app_root

def test_get_app_root_frozen(monkeypatch):
    # 模拟打包环境
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    
    mock_exe_path = "/mock/path/PhoneMic.exe"
    monkeypatch.setattr(sys, "executable", mock_exe_path)
    
    # 获取打包根目录
    root = get_app_root()
    
    # 验证是否返回了可执行文件所在的目录
    assert Path(root) == Path("/mock/path")
