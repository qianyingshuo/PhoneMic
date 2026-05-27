#!/usr/bin/env python3
"""
临时测试脚本：验证 IP 选择对话框 (IpSelector) 的功能。
用法：python test_ip_selector.py
依赖：PySide6（已安装）
"""

import sys
from typing import NamedTuple

# 模拟 IpCandidate 结构（正式代码中会从 utils.network 导入）
class IpCandidate(NamedTuple):
    ip: str
    description: str
    priority: int   # 越小越优先

from PySide6.QtWidgets import QApplication

# 尝试从实际项目中导入 IpSelector，若失败则使用下面模拟的导入路径
try:
    from phonemic.gui.ip_selector import IpSelector
except ImportError:
    # 如果正式模块尚未创建，这里提供一个简化版（实际应复制真实代码）
    # 为了避免重复代码，这里给出一个内联的临时实现（假设真实代码已按规范写）
    print("警告: 未找到 gui.ip_selector，请确保该模块已创建。")
    print("若您尚未编写 IpSelector，请先完成子任务 06.1 的代码实现。")
    sys.exit(1)

def main():
    app = QApplication(sys.argv)

    # 构造多个候选 IP（模拟 WiFi + 有线 + 虚拟网卡）
    candidates = [
        IpCandidate("192.168.1.105", "Intel(R) Wi-Fi 6 AX201", priority=1),
        IpCandidate("10.0.0.5", "Realtek PCIe GbE Family Controller", priority=2),
        IpCandidate("172.16.0.3", "VMware Virtual Ethernet Adapter", priority=10),
    ]

    # 显示对话框
    selector = IpSelector(candidates)
    result = selector.exec()

    if result:
        selected_ip = selector.get_selected_ip()
        if selected_ip:
            print(f"用户选择了 IP: {selected_ip}")
        else:
            print("用户点击了确定但没有选中任何项（理论上不应发生）")
    else:
        print("用户取消了选择或关闭了对话框，未选中任何 IP。")

    # 不执行 app.exec()，因为对话框已经模态运行并返回，测试结束
    # 可以正常退出
    sys.exit(0)

if __name__ == "__main__":
    main()