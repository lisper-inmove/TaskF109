import json
import socket
import struct
import time

from log_config import main_logger as logger
from protocol import Protocol
from timing import simple_timer


class Device:

    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name
        self.connected = False
        self.sock = None

    def connect(self):
        if self.connected:
            return
        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self.sock.connect((self.ip, self.port))
        logger.info(f"Device {self.name} connected to {self.ip}:{self.port}")
        self.connected = True

    def disconnect(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.connected = False

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
        self.sock.sendall(packet)
        self.recv()

    def recv(self):
        self.sock.recv(1024)
