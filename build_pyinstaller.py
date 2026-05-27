#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PhoneMic PyInstaller 打包脚本（备选方案）
用法: pack-env\Scripts\activate && python build_pyinstaller.py
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SPEC_FILE = PROJECT_ROOT / "build_pyinstaller.spec"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"


def run_pyinstaller():
    """执行 PyInstaller 打包命令"""
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",                       # 清理临时文件
        "--noconfirm",                   # 覆盖输出目录不询问
        "--log-level=INFO",              # 日志级别
        str(SPEC_FILE),
    ]
    print("Running PyInstaller with command:")
    print(" ".join(cmd))
    subprocess.check_call(cmd)


if __name__ == "__main__":
    if not SPEC_FILE.exists():
        print(f"Error: Spec file not found at {SPEC_FILE}", file=sys.stderr)
        sys.exit(1)
    run_pyinstaller()
    print(f"\n✅ Build succeeded! Output directory: {DIST_DIR}")