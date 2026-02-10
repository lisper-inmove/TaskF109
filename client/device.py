import json
import socket
import struct
import time

from log_config import main_logger as logger
from protocol import Protocol
from timing import simple_timer


class Device:

    def __init__(self, ip, port, name):
        self.__ip = ip
        self.__port = port
        self.__name = name
        self.__connected = False
        self.__sock = None
        self.__failed = 0

    @property
    def failed(self):
        return self.__failed

    @property
    def connected(self):
        return self.__connected

    @property
    def name(self):
        return self.__name

    def connect(self):
        if self.__connected:
            return
        self.__sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self.__sock.connect((self.__ip, self.__port))
        logger.info(
            f"Device {self.__name} connected to {self.__ip}:{self.__port}")
        self.__connected = True

    def disconnect(self):
        try:
            self.__connected = False
            self.__sock.shutdown(socket.SHUT_RDWR)
            self.__sock.close()
        except Exception as ex:
            logger.warning(f"Disconnect error: {ex}")

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
        self.__sock.sendall(packet)
        self.recv()

    def recv(self):
        self.__sock.recv(1024)

    def failed_incr(self):
        self.__failed += 1

    def failed_reset(self):
        self.__failed = 0
