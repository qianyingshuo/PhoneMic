#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# PhoneMic Windows 测试环境同步脚本 (sync_to_test.sh)
# 
# 功能：将当前开发目录的代码安全同步到 WSL 宿主机的 Windows 测试文件夹，
#       在清理掉废旧代码的同时，保留目标测试环境已有的虚拟环境 (.venv)。
# -----------------------------------------------------------------------------

set -euo pipefail

# 默认源路径与目标路径
SRC_DIR="/home/coding/workspace/PhoneMic/"
DST_DIR="/mnt/s/WSL/wsl_windows_test/PhoneMic/"

# 支持通过参数重载目标路径，如: ./sync_to_test.sh /custom/target/path
if [ $# -gt 0 ]; then
  DST_DIR="$1"
fi

# 确保路径以 / 结尾以符合 rsync 规范
[[ "$SRC_DIR" != */ ]] && SRC_DIR="$SRC_DIR/"
[[ "$DST_DIR" != */ ]] && DST_DIR="$DST_DIR/"

# 检查源目录是否存在
if [ ! -d "$SRC_DIR" ]; then
  echo "❌ 错误: 源项目目录 $SRC_DIR 不存在！"
  exit 1
fi

# 检查目标目录是否存在
if [ ! -d "$DST_DIR" ]; then
  echo "❌ 错误: 目标测试目录 $DST_DIR 不存在，请确认映射路径是否正确！"
  exit 1
fi

echo "=========================================================="
echo "🔄 开始进行 Windows 测试环境代码同步..."
echo "📂 源项目路径: $SRC_DIR"
echo "📂 目标同步区: $DST_DIR"
echo "=========================================================="

# 执行 rsync 同步：
# --delete: 删除目标目录中源目录没有的多余文件
# --exclude: 排除虚拟环境、Git 信息、智能体缓存及平台打包的 build/dist 目录
rsync -av --delete \
  --exclude='.venv/' \
  --exclude='venv/' \
  --exclude='.git/' \
  --exclude='.agents/' \
  --exclude='__pycache__/' \
  --exclude='.pytest_cache/' \
  --exclude='build/' \
  --exclude='dist/' \
  "$SRC_DIR" "$DST_DIR"

echo "=========================================================="
echo "🚀 同步完成！目标端的虚拟环境 (.venv) 已被安全留存。"
echo "=========================================================="
