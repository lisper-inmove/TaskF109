import os


class ProtocolHeader:

    heartbeat = bytes([0xFF, 0x01])
    set_voltage = bytes([0xFF, 0x02])
    start = 0xFF
    end = 0xFE


class Protocol:

    def __init__(self):
        pass

    @classmethod
    def heartbeat(cls):
        msg = bytearray()
        msg.extend(ProtocolHeader.heartbeat)
        msg.append(ProtocolHeader.end)
        return msg

    @classmethod
    def set_voltage(cls, voltage):
        msg = bytearray()
        msg.extend(ProtocolHeader.set_voltage)
        msg.append(0x00)
        msg.append(0x01)
        msg.append((voltage >> 8) & 0xFF)
        msg.append(voltage & 0xFF)
        msg.append(ProtocolHeader.end)
        return msg

    @classmethod
    def set_multi_voltage(cls, voltages):
        msg = bytearray()
        msg.extend(ProtocolHeader.set_voltage)
        length = len(voltages)
        msg.append((length >> 8) & 0xFF)
        msg.append(length & 0xFF)
        min_v = int(os.environ.get('VOLTAGE_MIN', 0))
        max_v = int(os.environ.get('VOLTAGE_MAX', 20000))
        for voltage in voltages:
            if not (min_v <= voltage <= max_v):
                raise ValueError(
                    f"Voltage {voltage} out of range ({min_v}~{max_v} mV)")
            msg.append((voltage >> 8) & 0xFF)
            msg.append(voltage & 0xFF)
        msg.append(ProtocolHeader.end)
        return msg


if __name__ == '__main__':
    msg = Protocol.set_voltage(10)
    for value in msg:
        print(hex(value), end=",")
    print("\n")
    msg = Protocol.set_multi_voltage([10, 20, 19999])
    for value in msg:
        print(hex(value), end=",")
