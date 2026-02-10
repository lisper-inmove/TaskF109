import socket
import time
from typing import Dict

from PyQt5.QtCore import QThread, QTimer, pyqtSignal

from device import Device
from log_config import heartbeat_logger as logger


class HeartbeatThread(QThread):
    """心跳线程"""

    def __init__(self, interval=5):
        super().__init__()
        self.interval = interval
        self.running = True
        self.devices: Dict[Device] = {}

    def run(self):
        """线程主函数"""
        while self.running:
            try:
                for _, device in self.devices.items():
                    logger.info(f"Send heartbeat to device: {device.name}")
                    device.send_heartbeat()
            except Exception as e:
                logger.info("Send heartbeat failed: {}", e)
            time.sleep(self.interval)

    def stop(self):
        """停止心跳线程"""
        self.running = False
        self.wait()

    def add_device(self, device):
        """添加设备到心跳列表"""
        self.devices.update({device.name: device})

    def remove_device(self, device):
        """从心跳列表移除设备"""
        if self.devices.get(device.name):
            del self.devices[device.name]
