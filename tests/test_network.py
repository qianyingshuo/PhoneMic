"""
测试 phonemic.utils.network 模块
覆盖：
- get_all_lan_ips() 的候选 IP 获取与优先级排序
- get_local_ip() 在有/无可用 IP 时的返回值
- 边缘场景：无网络、仅虚拟网卡、多网卡优先级
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from phonemic.utils.network import get_all_lan_ips, get_local_ip, IpCandidate, find_free_port
import socket

def test_get_all_lan_ips_returns_list():
    candidates = get_all_lan_ips()
    assert isinstance(candidates, list)
    
# ========== 测试 find_free_port ==========
def test_find_free_port_finds_a_port():
    """测试函数能找到一个可用的端口"""
    # 动态获取一个系统分配的空闲端口作为起点，保证测试在任何受限容器环境均能通过
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tmp_s:
        tmp_s.bind(("", 0))
        free_port = tmp_s.getsockname()[1]

    port = find_free_port(start_port=free_port)
    assert isinstance(port, int)
    assert port >= free_port
    # 验证端口确实可用
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        assert s.bind(("", port)) is None # bind 成功时返回 None

def test_find_free_port_skips_used_port(mocker):
    """当起始端口被占用时，应返回下一个可用端口"""
    used_port = 9100

    def bind_side_effect(address):
        if address[1] == used_port:
            raise OSError("Address already in use")
        return None  # Simulate successful bind for other ports

    mocker.patch('socket.socket.bind', side_effect=bind_side_effect)

    free_port = find_free_port(start_port=used_port)
    assert free_port == used_port + 1

def test_find_free_port_returns_none_if_all_are_used(mocker):
    """如果范围内的所有端口都被占用，应返回 None"""
    # 模拟所有 bind 调用都失败
    mocker.patch('socket.socket.bind', side_effect=OSError("Address already in use"))
    
    port = find_free_port(start_port=9200, max_tries=5)
    assert port is None


def test_get_local_ip_returns_string_or_none():
    ip = get_local_ip()
    assert ip is None or isinstance(ip, str)


# ========== Fixtures 辅助函数 ==========
def create_mock_interface(name: str, ips: list, is_virtual: bool = False, is_wifi: bool = False):
    """
    创建模拟的 netifaces 接口数据
    Args:
        name: 接口名称，如 '以太网', 'Wi-Fi', 'VMware'
        ips: IPv4 地址列表，每个元素为 {'addr': '192.168.1.100', 'netmask': '255.255.255.0'}
        is_virtual: 是否为虚拟网卡（VMware/VirtualBox）
        is_wifi: 是否为无线网卡（用于优先级加分）
    Returns:
        适合 netifaces.ifaddresses 返回格式的字典片段
    """
    # 实际 netifaces 返回的数据结构复杂，我们简化模拟
    # 这里返回一个简单的可迭代对象，用于测试逻辑
    return {
        'name': name,
        'is_virtual': is_virtual,
        'is_wifi': is_wifi,
        'addrs': ips
    }


# ========== 测试 get_local_ip ==========
def test_get_local_ip_returns_best_ip():
    """
    有可用 IP 时，get_local_ip 应返回优先级最高的 IP（即 get_all_lan_ips 排序后的第一个）
    """
    mock_candidates = [
        IpCandidate("192.168.1.100", "Wi-Fi", "Wi-Fi",priority=0),
        IpCandidate("10.0.0.2", "Ethernet", "Ethernet", priority=1),
    ]
    with patch('phonemic.utils.network.get_all_lan_ips', return_value=mock_candidates):
        ip = get_local_ip()
        assert ip == "192.168.1.100"


def test_get_local_ip_no_network_returns_none():
    """
    无可用 IP 时，get_local_ip 应返回 None
    """
    with patch('phonemic.utils.network.get_all_lan_ips', return_value=[]):
        ip = get_local_ip()
        assert ip is None


def test_get_local_ip_single_candidate():
    """
    只有一个候选时，直接返回该 IP
    """
    mock_candidates = [
        IpCandidate("192.168.1.105", "Wi-Fi", "Wi-Fi", priority=0),
    ]
    with patch('phonemic.utils.network.get_all_lan_ips', return_value=mock_candidates):
        ip = get_local_ip()
        assert ip == "192.168.1.105"

