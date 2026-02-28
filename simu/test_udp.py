#!/usr/bin/env python3
"""测试 UDP 服务器功能"""

import socket
import struct
import json
import time

def pack_message(data):
    """打包消息"""
    if isinstance(data, dict):
        data_bytes = json.dumps(data).encode('utf-8')
    else:
        data_bytes = str(data).encode('utf-8')

    header = struct.pack('!I', len(data_bytes))
    return header + data_bytes

def unpack_message(data):
    """解包消息"""
    if len(data) < 4:
        return None

    data_length = struct.unpack('!I', data[:4])[0]
    if len(data) < 4 + data_length:
        return None

    data_bytes = data[4:4 + data_length]
    try:
        return json.loads(data_bytes.decode('utf-8'))
    except:
        return data_bytes.decode('utf-8')

def test_udp_server():
    """测试 UDP 服务器"""
    print("测试 UDP 服务器...")

    # 创建 UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)

    server_address = ('127.0.0.1', 9999)

    try:
        # 发送测试消息
        test_message = {"type": "test", "content": "Hello UDP Server"}
        packed_data = pack_message(test_message)

        print(f"发送消息: {test_message}")
        sock.sendto(packed_data, server_address)

        # 接收响应
        data, addr = sock.recvfrom(4096)
        response = unpack_message(data)

        print(f"收到响应: {response}")
        print("✓ UDP 服务器测试通过")

        return True

    except socket.timeout:
        print("✗ 超时：服务器未响应")
        return False
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False
    finally:
        sock.close()

if __name__ == "__main__":
    test_udp_server()
