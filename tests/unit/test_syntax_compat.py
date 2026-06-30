import re
from pathlib import Path

def test_no_nested_same_quotes_in_fstrings():
    # 静态检查代码中是否存在 f-string 嵌套同类双引号的问题以保证 Python 3.11 兼容性
    file_path = Path("phonemic/utils/settings_manager.py")
    content = file_path.read_text(encoding="utf-8")
    
    # 匹配模式：f" 包含 { 包含 " 包含 " 包含 } 包含 "
    # 例如 f"default lan is {default["language"]}"
    bad_line_pattern = r'f"[^"]*\{[^"}]*"[^"}]*"[^}]*\}[^"]*"'
    matches = re.findall(bad_line_pattern, content)
    
    assert len(matches) == 0, f"发现不兼容的 f-string 同类双引号嵌套语法（Python 3.11 下会报错）: {matches}"
