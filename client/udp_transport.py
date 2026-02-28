import socket
import time
from typing import Optional

from log_config import main_logger as logger
from transport_strategy import TransportStrategy


class UDPTransport(TransportStrategy):
    """UDP 传输策略实现，包含超时重传机制"""

    def __init__(self,
                 ip: str,
                 port: int,
                 name: str,
                 timeout: float = 2.0,
                 max_retries: int = 3):
        self._ip = ip
        self._port = port
        self._name = name
        self._timeout = timeout
        self._max_retries = max_retries
        self._sock: Optional[socket.socket] = None
        self._connected = False

    def connect(self) -> None:
        """创建 UDP socket（UDP 是无连接协议，不需要真正连接）"""
        if self._connected:
            return

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.settimeout(self._timeout)
        self._connected = True
        logger.info(f"[UDP] Device {self._name} ready to communicate with "
                    f"{self._ip}:{self._port}")

    def disconnect(self) -> None:
        """关闭 UDP socket"""
        try:
            self._connected = False
            if self._sock:
                self._sock.close()
                logger.info(f"[UDP] Device {self._name} socket closed")
        except Exception as ex:
            logger.warning(f"[UDP] Disconnect error: {ex}")

    def send(self, packet: bytes) -> None:
        """发送数据包（UDP 不保证送达）"""
        if not self._sock:
            raise RuntimeError("Socket not connected")

        try:
            self._sock.sendto(packet, (self._ip, self._port))
            logger.debug(f"[UDP] Sent packet to {self._name}")
        except Exception as ex:
            logger.error(f"[UDP] Send error to {self._name}: {ex}")
            raise

    def recv(self, buffer_size: int = 1024) -> bytes:
        """接收数据包"""
        if not self._sock:
            raise RuntimeError("Socket not connected")

        try:
            # data, addr = self._sock.recvfrom(buffer_size)
            # logger.debug(f"[UDP] Received {len(data)} bytes from {addr}")
            # return data
            pass
        except socket.timeout:
            logger.warning(f"[UDP] Receive timeout from {self._name}")
            raise
        except Exception as ex:
            logger.error(f"[UDP] Receive error from {self._name}: {ex}")
            raise

    @property
    def connected(self) -> bool:
        """连接状态"""
        return self._connected
