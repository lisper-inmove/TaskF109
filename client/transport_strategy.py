from abc import ABC, abstractmethod
from typing import Tuple


class TransportStrategy(ABC):
    """传输策略抽象基类，定义统一的传输接口"""

    @abstractmethod
    def connect(self) -> None:
        """建立连接"""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass

    @abstractmethod
    def send(self, packet: bytes) -> None:
        """发送数据包"""
        pass

    @abstractmethod
    def recv(self, buffer_size: int = 1024) -> bytes:
        """接收数据包"""
        pass

    @property
    @abstractmethod
    def connected(self) -> bool:
        """连接状态"""
        pass
