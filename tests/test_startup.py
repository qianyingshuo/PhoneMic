import sys
import pytest
from unittest.mock import MagicMock
from PySide6.QtWidgets import QApplication

# 提前导入 PhoneMic 模块，以便 patch.object 使用
import phonemic.PhoneMic


def test_single_ip_no_dialog(mocker, qapp):
    app = QApplication.instance()
    mocker.patch.object(app, 'exec', return_value=0)

    # 使用 patch.object 替换字符串路径
    mock_get_ips = mocker.patch.object(phonemic.PhoneMic, 'get_all_lan_ips')
    mock_find_port = mocker.patch.object(phonemic.PhoneMic, 'find_free_port', return_value=8008)
    mock_IpSelector = mocker.patch.object(phonemic.PhoneMic, 'IpSelector')
    mock_start_server = mocker.patch.object(phonemic.PhoneMic, 'start_server')
    mock_Dashboard = mocker.patch.object(phonemic.PhoneMic, 'Dashboard')
    mocker.patch.object(phonemic.PhoneMic, 'wait_for_server', return_value=True)
    mocker.patch('threading.Thread')

    from phonemic.utils.network import IpCandidate
    single_candidate = IpCandidate(
        ip="192.168.1.100", interface_name="Wi-Fi",
        description="Intel Wi-Fi 6", priority=0
    )
    mock_get_ips.return_value = [single_candidate]

    with pytest.raises(SystemExit) as exc_info:
        phonemic.PhoneMic.main()   # 直接调用，无需再次导入
    assert exc_info.value.code == 0

    mock_IpSelector.assert_not_called()
    mock_find_port.assert_called_once()
    mock_start_server.assert_called_once_with("192.168.1.100", 8008, mocker.ANY)
    mock_Dashboard.assert_called_once_with("192.168.1.100", 8008)
    mock_Dashboard.return_value.show.assert_called_once()


def test_multi_ip_user_confirm(mocker, qapp):
    app = QApplication.instance()
    mocker.patch.object(app, 'exec', return_value=0)

    mock_get_ips = mocker.patch.object(phonemic.PhoneMic, 'get_all_lan_ips')
    mock_find_port = mocker.patch.object(phonemic.PhoneMic, 'find_free_port', return_value=8008)
    mock_IpSelector = mocker.patch.object(phonemic.PhoneMic, 'IpSelector')
    mock_IpSelector.Accepted = 1
    mock_start_server = mocker.patch.object(phonemic.PhoneMic, 'start_server')
    mock_Dashboard = mocker.patch.object(phonemic.PhoneMic, 'Dashboard')
    mocker.patch.object(phonemic.PhoneMic, 'wait_for_server', return_value=True)
    mocker.patch('threading.Thread')
    mocker.patch('multiprocessing.Queue')
    mocker.patch.object(phonemic.PhoneMic, 'QueueSignals')

    from phonemic.utils.network import IpCandidate
    candidates = [
        IpCandidate(ip="192.168.1.100", interface_name="Wi-Fi", description="Intel Wi-Fi 6", priority=0),
        IpCandidate(ip="10.0.0.2", interface_name="Ethernet", description="Realtek PCIe", priority=1),
    ]
    mock_get_ips.return_value = candidates

    mock_selector_instance = mock_IpSelector.return_value
    mock_selector_instance.exec.return_value = 1
    mock_selector_instance.get_selected_ip.return_value = "10.0.0.2"

    with pytest.raises(SystemExit) as exc_info:
        phonemic.PhoneMic.main()
    assert exc_info.value.code == 0

    mock_IpSelector.assert_called_once_with(candidates)
    mock_find_port.assert_called_once()
    mock_start_server.assert_called_once_with("10.0.0.2", 8008, mocker.ANY)
    mock_Dashboard.assert_called_once_with("10.0.0.2", 8008)


def test_multi_ip_user_cancel(mocker, qapp):
    app = QApplication.instance()
    mocker.patch.object(app, 'exec', return_value=0)

    mock_get_ips = mocker.patch.object(phonemic.PhoneMic, 'get_all_lan_ips')
    mock_IpSelector = mocker.patch.object(phonemic.PhoneMic, 'IpSelector')
    mock_start_server = mocker.patch.object(phonemic.PhoneMic, 'start_server')
    mocker.patch('threading.Thread')

    from phonemic.utils.network import IpCandidate
    candidates = [
        IpCandidate(ip="192.168.1.100", interface_name="Wi-Fi", description="Intel Wi-Fi 6", priority=0),
        IpCandidate(ip="10.0.0.2", interface_name="Ethernet", description="Realtek PCIe", priority=1),
    ]
    mock_get_ips.return_value = candidates

    mock_selector_instance = mock_IpSelector.return_value
    mock_selector_instance.exec.return_value = 0

    with pytest.raises(SystemExit) as exc_info:
        phonemic.PhoneMic.main()
    assert exc_info.value.code == 0

    mock_start_server.assert_not_called()


def test_no_ip_error_and_exit(mocker, qapp):
    app = QApplication.instance()
    mocker.patch.object(app, 'exec', return_value=0)

    mock_get_ips = mocker.patch.object(phonemic.PhoneMic, 'get_all_lan_ips', return_value=[])
    mock_QMessageBox = mocker.patch.object(phonemic.PhoneMic, 'QMessageBox')
    mock_start_server = mocker.patch.object(phonemic.PhoneMic, 'start_server')

    with pytest.raises(SystemExit) as exc_info:
        phonemic.PhoneMic.main()
    assert exc_info.value.code == 1

    mock_QMessageBox.critical.assert_called_once()
    assert "未检测到可用局域网IP" in mock_QMessageBox.critical.call_args[0][2]
    mock_start_server.assert_not_called()


def test_no_free_port_error_and_exit(mocker, qapp):
    """测试找不到可用端口时，应显示错误并退出"""
    app = QApplication.instance()
    mocker.patch.object(app, 'exec', return_value=0)

    mock_get_ips = mocker.patch.object(phonemic.PhoneMic, 'get_all_lan_ips')
    mock_find_port = mocker.patch.object(phonemic.PhoneMic, 'find_free_port', return_value=None)
    mock_QMessageBox = mocker.patch.object(phonemic.PhoneMic, 'QMessageBox')
    mock_start_server = mocker.patch.object(phonemic.PhoneMic, 'start_server')

    from phonemic.utils.network import IpCandidate
    mock_get_ips.return_value = [IpCandidate("192.168.1.100", "Wi-Fi", "Desc", 0)]

    with pytest.raises(SystemExit) as exc_info:
        phonemic.PhoneMic.main()
    assert exc_info.value.code == 1

    mock_find_port.assert_called_once()
    mock_QMessageBox.critical.assert_called_once()
    assert "未找到可用端口" in mock_QMessageBox.critical.call_args[0][2]
    mock_start_server.assert_not_called()