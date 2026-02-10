from typing import Dict

from device import Device


class Controller:

    def __init__(self):
        self.devices: Dict[str, Device] = {}

    def add_device(self, ip, port, name):
        if self.devices.get(name):
            return
        device = Device(ip, port, name)
        self.devices.update({name: device})
        return device

    def get_device(self, name):
        return self.devices.get(name)

    def remove_device(self, name):
        if self.devices.get(name):
            del self.devices[name]
