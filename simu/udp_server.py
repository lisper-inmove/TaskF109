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

    def stop(self):
        """停止服务器"""
        pass

    def get_server_stats(self) -> Dict:
        """获取服务器统计信息"""
        pass
