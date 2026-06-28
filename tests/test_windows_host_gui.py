#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 宿主机自动化 GUI 测试验证脚本
用于检测 PhoneMic 开发版在 Windows 下的最小化隐藏与关闭拦截逻辑是否按预期工作。
本脚本专门寻找标题带有 (Dev) 后缀的窗口，以防与您正常运行的 PhoneMic 生产程序冲突。
前提条件：
1. 宿主机已安装 Python 3.x
2. 宿主机已安装 pywin32 库：pip install pywin32
3. PhoneMic 独立开发测试版程序已经在 Windows 宿主机上正常启动。
"""

import sys
import time

try:
    import win32gui
    import win32con
except ImportError:
    print("错误：未检测到 pywin32 依赖，请在宿主机执行: pip install pywin32")
    sys.exit(1)


def test_windows_gui():
    print("=" * 60)
    print("      PhoneMic Windows 宿主机 GUI 自动化验证脚本 (Dev版)       ")
    print("=" * 60)

    # 1. 查找窗口句柄（匹配测试版窗口）
    title = "PhoneMic - 主界面 (Dev)"
    print(f"正在寻找目标开发版窗口：'{title}'...")
    hwnd = win32gui.FindWindow(None, title)

    if hwnd == 0:
        # 兜底查找英文环境开发版窗口
        title_en = "PhoneMic - Main Window (Dev)"
        hwnd = win32gui.FindWindow(None, title_en)

    if hwnd == 0:
        print("❌ 错误：未找到目标开发版窗口！")
        print("   请确保您运行的是本次编译的开发测试版本，且窗口标题包含 ' (Dev)' 后缀。")
        sys.exit(1)

    print(f"✅ 成功找到开发版窗口，句柄 ID: {hwnd}")
    time.sleep(1)

    # 2. 模拟最小化事件并验证隐藏
    print("\n--- 步骤 1: 验证最小化隐藏 ---")
    print("发送窗口最小化消息(SC_MINIMIZE)...")
    win32gui.PostMessage(hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0)
    time.sleep(2)  # 等待窗口处理事件

    # 最小化后，窗口应当被隐藏（IsWindowVisible 返回 False），而句柄应存活（进程未退出）
    if win32gui.IsWindowVisible(hwnd):
        print("❌ 失败：窗口最小化后依然处于可见状态，未在任务栏隐藏！")
        sys.exit(1)
    
    if not win32gui.IsWindow(hwnd):
        print("❌ 失败：窗口发送最小化消息后，开发版进程意外退出了！")
        sys.exit(1)

    print("✅ 成功：开发版主窗口已从任务栏和切窗视图隐藏，且后台进程保持运行。")
    time.sleep(1)

    # 3. 恢复窗口显示
    print("\n--- 步骤 2: 验证从托盘唤醒恢复显示 ---")
    print("通过消息恢复显示窗口(SW_SHOW & SW_RESTORE)...")
    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    # 强制将窗口带入前台并激活
    try:
        win32gui.SetForegroundWindow(hwnd)
    except Exception:
        pass
    time.sleep(2)

    if not win32gui.IsWindowVisible(hwnd):
        print("❌ 失败：开发版主窗口恢复显示后，依然不可见！")
        sys.exit(1)

    print("✅ 成功：开发版主窗口恢复正常显示，并重新获得焦点。")
    time.sleep(1)

    # 4. 模拟右上角 (X) 关闭按钮并验证拦截
    print("\n--- 步骤 3: 验证点击关闭(X)转换为隐藏 ---")
    print("发送关闭消息(WM_CLOSE)...")
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    time.sleep(2)

    # 关闭按钮应被拦截转换为隐藏，窗口不可见，但句柄依旧存活
    if win32gui.IsWindowVisible(hwnd):
        print("❌ 失败：点击关闭(X)后窗口依然可见，未能成功拦截并隐藏！")
        sys.exit(1)

    if not win32gui.IsWindow(hwnd):
        print("❌ 失败：点击关闭(X)后程序直接退出了，应该拦截并保持后台运行！")
        sys.exit(1)

    print("✅ 成功：开发版主窗口点击关闭(X)后成功转换为隐藏，且后台进程与连接保持正常。")
    time.sleep(1)

    # 5. 提示用户手动触发退出
    print("\n--- 步骤 4: 验证托盘右键退出进程 ---")
    print("⚠️ 请在右下角开发版托盘图标上【右键 -> 点击退出】来完成测试...")
    
    # 轮询 15 秒检查窗口句柄是否失效
    for i in range(15):
        if not win32gui.IsWindow(hwnd):
            print("✅ 成功：检测到开发版窗口句柄已销毁，程序已彻底退出。")
            print("=" * 60)
            print("🎉 恭喜！PhoneMic 开发测试版通过宿主机实机验证！")
            print("=" * 60)
            sys.exit(0)
        time.sleep(1)
        
    print("❌ 失败：等待超时，程序未能彻底退出（句柄依然存活）。")
    sys.exit(1)


if __name__ == "__main__":
    test_windows_gui()
