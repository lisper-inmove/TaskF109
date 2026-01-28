import socket

from loguru import logger


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

    def send(self, msg):
        data = bytearray([0x01, 0x02, 0x03])
        self.sock.sendall(data)
        logger.info(f"Send Data to server: {data}")

    def recv(self):
        data = self.sock.recv(1024)
        logger.info(f"Received data: {data}")
