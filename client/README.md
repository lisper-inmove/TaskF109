# protocol test

    `python
    if __name__ == '__main__':
        msg = Protocol.set_voltage(10)
        for value in msg:
            print(hex(value), end=",")
        print("\n")
        # 0xff,0x2,0x0,0x1,0x0,0xa,0xfe
        msg = Protocol.set_multi_voltage([10, 20, 19999])
        for value in msg:
            print(hex(value), end=",")
        # 0xff,0x2,0x0,0x3,0x0,0xa,0x0,0x14,0x4e,0x1f,0xfe
    `
