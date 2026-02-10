import json
import socket
import struct
import time


def test_tcp_server(host="127.0.0.1", port=8888):
    """测试TCP服务器"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 连接服务器
        client_socket.connect((host, port))
        print(f"已连接到服务器 {host}:{port}")

        # 测试发送字符串
        test_messages = [
            "Hello, Server!", {
                "action": "ping",
                "timestamp": time.time()
            }, ["item1", "item2", "item3"], b"Binary data test"
        ]

        for i, message in enumerate(test_messages):
            # 打包数据
            if isinstance(message, (dict, list)):
                data = json.dumps(message).encode('utf-8')
            elif isinstance(message, str):
                data = message.encode('utf-8')
            else:
                data = message

            # 添加长度头
            header = struct.pack('!I', len(data))
            packet = header + data

            # 发送数据
            client_socket.sendall(packet)
            print(f"发送消息 {i+1}: {message}")

            # 接收响应
            response_header = client_socket.recv(4)
            if not response_header:
                print("服务器断开连接")
                break

            response_length = struct.unpack('!I', response_header)[0]
            response_data = client_socket.recv(response_length)

            # 解析响应
            try:
                response = json.loads(response_data.decode('utf-8'))
                print(f"收到响应: {response}")
            except:
                print(f"收到原始响应: {response_data}")

            time.sleep(1)

    except Exception as e:
        print(f"连接失败: {e}")
    finally:
        client_socket.close()
        print("连接已关闭")


if __name__ == "__main__":
    # 测试多个端口
    # for port in [8888, 8889, 8890]:
    #     print(f"\n测试端口 {port}...")
    #     test_tcp_server("192.168.200.27", port)
    test_tcp_server("192.168.200.27", 8888)
