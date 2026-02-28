import os
import socket

from log_config import main_logger as logger
from protocol import Protocol
from tcp_transport import TCPTransport
from transport_strategy import TransportStrategy
from udp_transport import UDPTransport


class Device:

    def __init__(self, ip, port, name):
        self.__ip = ip
        self.__port = port
        self.__name = name
        self.__protocol_type = os.environ.get("PROTOCOL_TYPE", "udp").lower()
        self.__failed = 0

        # 根据协议类型创建传输策略
        if self.__protocol_type == 'tcp':
            self.__transport: TransportStrategy = TCPTransport(ip, port, name)
        elif self.__protocol_type == 'udp':
            self.__transport: TransportStrategy = UDPTransport(ip, port, name)
        else:
            raise ValueError(f"Unsupported protocol type: {protocol_type}")

    @property
    def failed(self):
        return self.__failed

    @property
    def connected(self):
        return self.__transport.connected

    @property
    def name(self):
        return self.__name

    def connect(self):
        """委托给传输策略"""
        self.__transport.connect()

    def disconnect(self):
        """委托给传输策略"""
        self.__transport.disconnect()

    def send_heartbeat(self):
        msg = Protocol.heartbeat()
        self.send(msg)

    def send_set_voltage(self, voltage):
        msg = Protocol.set_voltage(voltage)
        logger.info(f"Send set voltage: {msg}")
        self.send(msg)

    def send_multi_voltage(self, voltages):
        msg = Protocol.set_multi_voltage(voltages)
        logger.info(f"Send set multi voltage: {msg}")
        self.send(msg)

    def send(self, packet):
        """发送数据包并接收响应"""
        try:
            self.__transport.send(packet)
            return self.recv()
        except socket.timeout:
            logger.warning(f"[{self.__name}] Receive timeout after send")
            raise
        except Exception as ex:
            logger.error(f"[{self.__name}] Send/recv error: {ex}")
            raise

    def recv(self):
        """委托给传输策略"""
        return self.__transport.recv()

    def failed_incr(self):
        self.__failed += 1

    def failed_reset(self):
        self.__failed = 0
