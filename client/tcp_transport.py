import socket
from typing import Optional

from log_config import main_logger as logger
from transport_strategy import TransportStrategy


class TCPTransport(TransportStrategy):
    """TCP 传输策略实现"""

    def __init__(self, ip: str, port: int, name: str):
        self._ip = ip
        self._port = port
        self._name = name
        self._sock: Optional[socket.socket] = None
        self._connected = False

    def connect(self) -> None:
        """建立 TCP 连接"""
        if self._connected:
            return

        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(5.0)  # 设置超时
            self._sock.connect((self._ip, self._port))
            self._connected = True
            logger.info(
                f"[TCP] Device {self._name} connected to {self._ip}:{self._port}"
            )
        except socket.timeout:
            logger.error(f"[TCP] Connection timeout to {self._ip}:{self._port}")
            if self._sock:
                self._sock.close()
            raise
        except Exception as ex:
            logger.error(f"[TCP] Connection failed to {self._ip}:{self._port}: {ex}")
            if self._sock:
                self._sock.close()
            raise

    def disconnect(self) -> None:
        """断开 TCP 连接"""
        try:
            self._connected = False
            if self._sock:
                self._sock.shutdown(socket.SHUT_RDWR)
                self._sock.close()
                logger.info(f"[TCP] Device {self._name} disconnected")
        except Exception as ex:
            logger.warning(f"[TCP] Disconnect error: {ex}")

    def send(self, packet: bytes) -> None:
        """发送数据包"""
        if not self._sock:
            raise RuntimeError("Socket not connected")
        self._sock.sendall(packet)

    def recv(self, buffer_size: int = 1024) -> bytes:
        """接收数据包"""
        if not self._sock:
            raise RuntimeError("Socket not connected")
        return self._sock.recv(buffer_size)

    @property
    def connected(self) -> bool:
        """连接状态"""
        return self._connected
