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

    def stop(self):
        """停止服务器"""
        pass

    def get_server_stats(self) -> Dict:
        """获取服务器统计信息"""
        pass
