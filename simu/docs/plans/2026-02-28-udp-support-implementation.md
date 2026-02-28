# UDP 服务器支持实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为仿真服务器添加 UDP 协议支持，使其能够处理来自客户端的 UDP 数据包

**Architecture:** 创建独立的 UDPServer 类（与 TCPServer 平行），使用单个 UDP socket 接收所有客户端的数据包并立即响应。复用现有的 ByteStreamProtocol 进行消息打包/解包。

**Tech Stack:** Python 3, socket (UDP), threading, ByteStreamProtocol

---

## Task 1: 创建 UDPServer 基础结构

**Files:**
- Create: `simu/udp_server.py`

**Step 1: 创建 UDPServer 类骨架**

创建文件 `simu/udp_server.py`，包含基础类结构：

```python
# udp_server.py
import socket
import threading
import time
from typing import Dict, Optional, Callable, Any
from config import Config
from protocol import ByteStreamProtocol
from utils.logger import setup_logger


class UDPServer:
    """UDP 服务器"""

    def __init__(self, host: str = "0.0.0.0", port: int = 8888, config: Config = None):
        """
        初始化 UDP 服务器

        Args:
            host: 监听地址
            port: 监听端口
            config: 配置对象
        """
        self.host = host
        self.port = port
        self.config = config or Config()

        # 服务器状态
        self.running = False
        self.server_socket: Optional[socket.socket] = None
        self.server_thread: Optional[threading.Thread] = None

        # 协议处理器
        self.protocol = ByteStreamProtocol(
            header_size=self.config.get("protocol.header_size", 4),
            encoding=self.config.get("protocol.encoding", "utf-8")
        )

        # 消息处理回调
        self.message_callback: Optional[Callable] = None

        # 统计信息
        self.stats = {
            "start_time": 0,
            "total_packets": 0,
            "bytes_received": 0,
            "bytes_sent": 0
        }

        # 日志记录器
        self.logger = setup_logger(
            name=f"udp_server_{port}",
            level=self.config.get("logging.level", "INFO"),
            log_file=self.config.get("logging.file")
        )

    def set_message_callback(self, callback: Callable[[Any, tuple], Any]):
        """设置消息处理回调函数"""
        self.message_callback = callback

    def start(self):
        """启动服务器"""
        pass

    def stop(self):
        """停止服务器"""
        pass

    def get_server_stats(self) -> Dict:
        """获取服务器统计信息"""
        pass
```

**Step 2: 验证文件创建**

运行：`python -m py_compile simu/udp_server.py`
预期：无语法错误

**Step 3: 提交**

```bash
git add simu/udp_server.py
git commit -m "feat: add UDPServer class skeleton"
```

---

## Task 2: 实现 UDPServer 启动逻辑

**Files:**
- Modify: `simu/udp_server.py`

**Step 1: 实现 start() 方法**

在 `udp_server.py` 中实现 `start()` 方法：

```python
def start(self):
    """启动服务器"""
    if self.running:
        self.logger.warning("服务器已在运行中")
        return

    try:
        # 创建 UDP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 绑定地址和端口
        self.server_socket.bind((self.host, self.port))

        # 设置超时避免阻塞
        self.server_socket.settimeout(1.0)

        # 设置服务器为运行状态
        self.running = True
        self.stats["start_time"] = time.time()

        # 启动服务器线程
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()

        self.logger.info(f"UDP 服务器已启动，监听 {self.host}:{self.port}")

    except Exception as e:
        self.logger.error(f"启动服务器失败: {e}")
        self.running = False
        raise
```

**Step 2: 验证语法**

运行：`python -m py_compile simu/udp_server.py`
预期：无语法错误

**Step 3: 提交**

```bash
git add simu/udp_server.py
git commit -m "feat: implement UDPServer start method"
```

---

## Task 3: 实现 UDPServer 主循环

**Files:**
- Modify: `simu/udp_server.py`

**Step 1: 实现 _run_server() 方法**

在 `udp_server.py` 中添加 `_run_server()` 方法：

```python
def _run_server(self):
    """运行服务器主循环"""
    self.logger.info("UDP 服务器主循环已启动")

    while self.running:
        try:
            # 接收数据包
            data, client_address = self.server_socket.recvfrom(4096)

            # 更新统计信息
            self.stats["total_packets"] += 1
            self.stats["bytes_received"] += len(data)

            # 处理数据包
            self._process_packet(data, client_address)

        except socket.timeout:
            # 超时继续循环
            continue
        except OSError as e:
            if self.running:
                self.logger.error(f"接收数据包时出错: {e}")
            break
        except Exception as e:
            self.logger.error(f"服务器循环异常: {e}")
            if self.running:
                time.sleep(0.1)

    self.logger.info("UDP 服务器主循环已退出")
```

**Step 2: 验证语法**

运行：`python -m py_compile simu/udp_server.py`
预期：无语法错误

**Step 3: 提交**

```bash
git add simu/udp_server.py
git commit -m "feat: implement UDPServer main loop"
```

---

## Task 4: 实现数据包处理逻辑

**Files:**
- Modify: `simu/udp_server.py`

**Step 1: 实现 _process_packet() 方法**

在 `udp_server.py` 中添加 `_process_packet()` 方法：

```python
def _process_packet(self, data: bytes, client_address: tuple):
    """
    处理接收到的数据包

    Args:
        data: 数据包内容
        client_address: 客户端地址 (ip, port)
    """
    try:
        # 解析数据包
        result = self.protocol.unpack(data)

        if result is None:
            self.logger.warning(f"数据包格式错误，来自 {client_address}")
            return

        message, _ = result

        # 调用消息处理回调
        if self.message_callback:
            response = self.message_callback(message, client_address)
        else:
            response = self._default_message_handler(message, client_address)

        # 发送响应
        self._send_response(response, client_address)

    except Exception as e:
        self.logger.error(f"处理数据包时出错: {e}")
        # 尝试发送错误响应
        try:
            error_response = self.protocol.create_response(
                success=False,
                message=f"数据处理错误: {e}"
            )
            self._send_response(error_response, client_address)
        except:
            pass

def _default_message_handler(self, message: Any, client_address: tuple) -> Dict:
    """
    默认消息处理器

    Args:
        message: 接收到的消息
        client_address: 客户端地址

    Returns:
        Dict: 响应数据
    """
    self.logger.info(f"处理来自 {client_address} 的消息: {message}")

    return self.protocol.create_response(
        success=True,
        message="消息处理成功",
        data={
            "original_message": message,
            "server_timestamp": time.time(),
            "server_port": self.port,
            "protocol": "UDP"
        }
    )

def _send_response(self, response: Any, client_address: tuple):
    """
    发送响应到客户端

    Args:
        response: 响应数据
        client_address: 客户端地址
    """
    try:
        packed_data = self.protocol.pack(response)
        self.server_socket.sendto(packed_data, client_address)

        # 更新统计信息
        self.stats["bytes_sent"] += len(packed_data)

        self.logger.debug(f"发送响应到 {client_address}")

    except Exception as e:
        self.logger.error(f"发送响应失败: {e}")
```

**Step 2: 验证语法**

运行：`python -m py_compile simu/udp_server.py`
预期：无语法错误

**Step 3: 提交**

```bash
git add simu/udp_server.py
git commit -m "feat: implement packet processing and response logic"
```

---

## Task 5: 实现 UDPServer 停止逻辑

**Files:**
- Modify: `simu/udp_server.py`

**Step 1: 实现 stop() 方法**

在 `udp_server.py` 中实现 `stop()` 方法：

```python
def stop(self):
    """停止服务器"""
    if not self.running:
        return

    self.logger.info("正在停止 UDP 服务器...")
    self.running = False

    # 关闭服务器套接字
    if self.server_socket:
        try:
            self.server_socket.close()
        except:
            pass

    # 等待服务器线程结束
    if self.server_thread and self.server_thread.is_alive():
        self.server_thread.join(timeout=5)

    self.logger.info("UDP 服务器已停止")
```

**Step 2: 验证语法**

运行：`python -m py_compile simu/udp_server.py`
预期：无语法错误

**Step 3: 提交**

```bash
git add simu/udp_server.py
git commit -m "feat: implement UDPServer stop method"
```

---

## Task 6: 实现统计信息方法

**Files:**
- Modify: `simu/udp_server.py`

**Step 1: 实现 get_server_stats() 方法**

在 `udp_server.py` 中实现 `get_server_stats()` 方法：

```python
def get_server_stats(self) -> Dict:
    """获取服务器统计信息"""
    stats = self.stats.copy()
    stats["uptime"] = time.time() - stats["start_time"] if self.running else 0
    stats["running"] = self.running
    stats["protocol"] = "UDP"
    stats["host"] = self.host
    stats["port"] = self.port
    return stats
```

**Step 2: 验证语法**

运行：`python -m py_compile simu/udp_server.py`
预期：无语法错误

**Step 3: 提交**

```bash
git add simu/udp_server.py
git commit -m "feat: implement get_server_stats method"
```

---

## Task 7: 修改 main.py 添加协议参数

**Files:**
- Modify: `simu/main.py`

**Step 1: 添加 --protocol 参数**

在 `main.py` 的 `main()` 函数中，修改参数解析部分：

```python
def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="TCP/UDP 服务器仿真工具")
    parser.add_argument("-p",
                        "--ports",
                        nargs="+",
                        type=int,
                        default=[9999],
                        help="监听的端口列表 (默认: 9999)")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址 (默认: 0.0.0.0)")
    parser.add_argument("--protocol",
                        choices=["tcp", "udp", "both"],
                        default="tcp",
                        help="协议类型 (默认: tcp)")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--stats-interval",
                        type=int,
                        default=10,
                        help="统计信息打印间隔 (秒，默认: 10)")
    parser.add_argument("--custom-handler",
                        action="store_true",
                        help="使用自定义消息处理器")

    args = parser.parse_args()
```

**Step 2: 验证语法**

运行：`python -m py_compile simu/main.py`
预期：无语法错误

**Step 3: 提交**

```bash
git add simu/main.py
git commit -m "feat: add --protocol argument to main.py"
```

---

## Task 8: 修改 MultiPortServerManager 支持 UDP

**Files:**
- Modify: `simu/main.py`

**Step 1: 导入 UDPServer**

在 `main.py` 顶部添加导入：

```python
from udp_server import UDPServer
```

**Step 2: 修改 MultiPortServerManager 类**

修改 `MultiPortServerManager` 类以支持 UDP：

```python
class MultiPortServerManager:
    """多端口服务器管理器"""

    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.servers: Dict[str, Any] = {}  # key: "protocol:port"
        self.running = False
        self.logger = setup_logger("server_manager")

    def start_servers(self, ports: List[int], host: str = "0.0.0.0", protocol: str = "tcp"):
        """
        启动多个端口的服务器

        Args:
            ports: 端口列表
            host: 监听地址
            protocol: 协议类型 (tcp/udp/both)
        """
        if self.running:
            self.logger.warning("服务器管理器已在运行中")
            return

        self.running = True

        for port in ports:
            # 根据协议类型启动服务器
            if protocol in ["tcp", "both"]:
                self._start_tcp_server(host, port)

            if protocol in ["udp", "both"]:
                self._start_udp_server(host, port)

        self.logger.info(f"已启动 {len(self.servers)} 个服务器实例")

    def _start_tcp_server(self, host: str, port: int):
        """启动 TCP 服务器"""
        try:
            server = TCPServer(host=host, port=port, config=self.config)
            server.start()
            self.servers[f"tcp:{port}"] = server
            self.logger.info(f"已启动 TCP 服务器: {host}:{port}")
        except Exception as e:
            self.logger.error(f"启动 TCP 服务器 {host}:{port} 失败: {e}")

    def _start_udp_server(self, host: str, port: int):
        """启动 UDP 服务器"""
        try:
            server = UDPServer(host=host, port=port, config=self.config)
            server.start()
            self.servers[f"udp:{port}"] = server
            self.logger.info(f"已启动 UDP 服务器: {host}:{port}")
        except Exception as e:
            self.logger.error(f"启动 UDP 服务器 {host}:{port} 失败: {e}")
```

**Step 3: 修改 stop_servers() 方法**

```python
def stop_servers(self):
    """停止所有服务器"""
    for server_key, server in self.servers.items():
        try:
            server.stop()
            self.logger.info(f"已停止服务器: {server_key}")
        except Exception as e:
            self.logger.error(f"停止服务器 {server_key} 失败: {e}")

    self.servers.clear()
    self.running = False
    self.logger.info("所有服务器已停止")
```

**Step 4: 修改 get_stats() 方法**

```python
def get_stats(self) -> Dict:
    """获取所有服务器的统计信息"""
    stats = {
        "total_servers": len(self.servers),
        "running": self.running,
        "servers": {}
    }

    for server_key, server in self.servers.items():
        stats["servers"][server_key] = server.get_server_stats()

    return stats
```

**Step 5: 验证语法**

运行：`python -m py_compile simu/main.py`
预期：无语法错误

**Step 6: 提交**

```bash
git add simu/main.py
git commit -m "feat: add UDP support to MultiPortServerManager"
```

---

## Task 9: 更新 main() 函数调用

**Files:**
- Modify: `simu/main.py`

**Step 1: 修改服务器启动调用**

在 `main()` 函数中，修改 `manager.start_servers()` 调用：

```python
# 启动服务器
print(f"启动服务器...")
print(f"监听地址: {args.host}")
print(f"监听端口: {args.ports}")
print(f"协议类型: {args.protocol}")
print(f"配置文件: {args.config or '使用默认配置'}")
print(f"统计间隔: {args.stats_interval}秒")
print(f"自定义处理器: {'是' if args.custom_handler else '否'}")
print("-" * 50)

try:
    # 启动服务器（传递协议参数）
    manager.start_servers(args.ports, args.host, args.protocol)

    # 设置自定义消息处理器
    if args.custom_handler:
        for server in manager.servers.values():
            server.set_message_callback(custom_message_handler)
        print("✓ 已启用自定义消息处理器")
```

**Step 2: 修改统计信息打印函数**

修改 `print_stats()` 函数以支持 UDP 统计：

```python
def print_stats(manager: MultiPortServerManager, interval: int = 10):
    """定期打印统计信息"""
    while manager.running:
        try:
            stats = manager.get_stats()

            print("\n" + "=" * 60)
            print(f"服务器统计信息 ({time.strftime('%Y-%m-%d %H:%M:%S')})")
            print("=" * 60)

            print(f"运行中的服务器: {stats['total_servers']}")

            for server_key, server_stats in stats["servers"].items():
                protocol, port = server_key.split(":")
                print(f"\n{protocol.upper()} 端口 {port}:")
                print(f"  运行时间: {server_stats['uptime']:.1f} 秒")

                if protocol == "tcp":
                    print(f"  总连接数: {server_stats['total_connections']}")
                    print(f"  当前连接: {server_stats['current_connections']}")
                    print(f"  最大并发: {server_stats['max_concurrent_connections']}")
                elif protocol == "udp":
                    print(f"  总数据包: {server_stats['total_packets']}")
                    print(f"  接收字节: {server_stats['bytes_received']}")
                    print(f"  发送字节: {server_stats['bytes_sent']}")

            print("=" * 60 + "\n")

            time.sleep(interval)

        except Exception as e:
            print(f"获取统计信息失败: {e}")
            time.sleep(interval)
```

**Step 3: 验证语法**

运行：`python -m py_compile simu/main.py`
预期：无语法错误

**Step 4: 提交**

```bash
git add simu/main.py
git commit -m "feat: update main function to support UDP protocol"
```

---

## Task 10: 手动测试验证

**Files:**
- Test: 手动测试

**Step 1: 测试 UDP 服务器启动**

运行：`cd simu && python main.py --ports 9999 --protocol udp`
预期：
- 服务器成功启动
- 日志显示 "UDP 服务器已启动，监听 0.0.0.0:9999"
- 统计信息正常显示

**Step 2: 测试 TCP 服务器（确保未破坏现有功能）**

运行：`cd simu && python main.py --ports 9999 --protocol tcp`
预期：
- TCP 服务器正常启动
- 功能未受影响

**Step 3: 测试同时运行 TCP 和 UDP**

运行：`cd simu && python main.py --ports 9999 --protocol both`
预期：
- 同时启动 TCP 和 UDP 服务器
- 统计信息显示两个服务器

**Step 4: 使用客户端测试 UDP 通信**

1. 启动 UDP 服务器：`cd simu && python main.py --ports 9999 --protocol udp`
2. 启动客户端：`cd ../client && python main.py`
3. 在 GUI 中选择 UDP 协议
4. 输入 IP 和端口 9999
5. 点击 Connect

预期：
- 客户端成功连接
- 服务器接收到数据包并响应
- 心跳机制正常工作
- 日志显示数据包收发记录

**Step 5: 提交测试结果**

如果所有测试通过，创建测试总结：

```bash
git add -A
git commit -m "test: verify UDP server functionality

- UDP server starts successfully
- TCP server still works (backward compatibility)
- Both protocols can run simultaneously
- Client can connect via UDP and exchange data
- Heartbeat mechanism works correctly"
```

---

## 完成清单

- [x] Task 1: 创建 UDPServer 基础结构
- [x] Task 2: 实现 UDPServer 启动逻辑
- [x] Task 3: 实现 UDPServer 主循环
- [x] Task 4: 实现数据包处理逻辑
- [x] Task 5: 实现 UDPServer 停止逻辑
- [x] Task 6: 实现统计信息方法
- [x] Task 7: 修改 main.py 添加协议参数
- [x] Task 8: 修改 MultiPortServerManager 支持 UDP
- [x] Task 9: 更新 main() 函数调用
- [x] Task 10: 手动测试验证

## 注意事项

1. **DRY 原则：** 复用 ByteStreamProtocol，避免重复代码
2. **YAGNI 原则：** 不添加当前不需要的功能（如客户端会话跟踪）
3. **错误处理：** 所有 socket 操作都有异常处理
4. **日志记录：** 关键操作都有日志记录
5. **向后兼容：** 不破坏现有 TCP 服务器功能
6. **频繁提交：** 每个任务完成后立即提交

## 测试建议

- 使用客户端的 UDPTransport 进行集成测试
- 测试多客户端并发场景
- 测试异常情况（端口占用、网络错误等）
- 验证统计信息准确性
