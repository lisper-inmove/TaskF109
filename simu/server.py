# server.py
import socket
import threading
import time
from typing import Dict, List, Optional, Callable, Any
from config import Config
from protocol import ByteStreamProtocol
from client_handler import ClientHandler
from utils.logger import setup_logger

class TCPServer:
    """TCP服务器"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8888, config: Config = None):
        """
        初始化TCP服务器
        
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
        
        # 客户端管理
        self.clients: Dict[str, ClientHandler] = {}
        self.client_lock = threading.Lock()
        
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
            "total_connections": 0,
            "current_connections": 0,
            "max_concurrent_connections": 0
        }
        
        # 日志记录器
        self.logger = setup_logger(
            name=f"server_{port}",
            level=self.config.get("logging.level", "INFO"),
            log_file=self.config.get("logging.file")
        )
    
    def set_message_callback(self, callback: Callable[[Any, tuple], Any]):
        """
        设置消息处理回调函数
        
        Args:
            callback: 回调函数，接收(消息数据, 客户端地址)返回响应数据
        """
        self.message_callback = callback
    
    def default_message_handler(self, message: Any, client_address: tuple) -> Dict:
        """
        默认消息处理器
        
        Args:
            message: 接收到的消息
            client_address: 客户端地址
            
        Returns:
            Dict: 响应数据
        """
        self.logger.info(f"处理来自 {client_address} 的消息: {message}")
        
        # 生成响应
        return self.protocol.create_response(
            success=True,
            message="消息处理成功",
            data={
                "original_message": message,
                "server_timestamp": time.time(),
                "server_port": self.port,
                "client_count": len(self.clients)
            }
        )
    
    def start(self):
        """启动服务器"""
        if self.running:
            self.logger.warning("服务器已在运行中")
            return
        
        try:
            # 创建服务器套接字
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # 绑定地址和端口
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.config.get("server.max_connections", 100))
            
            # 设置服务器为运行状态
            self.running = True
            self.stats["start_time"] = time.time()
            
            # 启动服务器线程
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            
            self.logger.info(f"TCP服务器已启动，监听 {self.host}:{self.port}")
            
        except Exception as e:
            self.logger.error(f"启动服务器失败: {e}")
            self.running = False
            raise
    
    def stop(self):
        """停止服务器"""
        if not self.running:
            return
        
        self.logger.info("正在停止服务器...")
        self.running = False
        
        # 关闭所有客户端连接
        with self.client_lock:
            client_ids = list(self.clients.keys())
            for client_id in client_ids:
                self.clients[client_id].stop()
            self.clients.clear()
        
        # 关闭服务器套接字
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        # 等待服务器线程结束
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)
        
        self.logger.info("服务器已停止")
    
    def _run_server(self):
        """运行服务器主循环"""
        while self.running:
            try:
                # 接受客户端连接
                client_socket, client_address = self.server_socket.accept()
                
                # 统计连接数
                self.stats["total_connections"] += 1
                current_conn = len(self.clients) + 1
                self.stats["current_connections"] = current_conn
                self.stats["max_concurrent_connections"] = max(
                    self.stats["max_concurrent_connections"], 
                    current_conn
                )
                
                # 创建客户端处理器
                client_handler = ClientHandler(
                    client_socket=client_socket,
                    client_address=client_address,
                    protocol=self.protocol,
                    on_message=self.message_callback or self.default_message_handler,
                    timeout=self.config.get("server.timeout", 30)
                )
                
                # 生成客户端ID
                client_id = f"{client_address[0]}:{client_address[1]}:{id(client_handler)}"
                
                # 添加到客户端列表
                with self.client_lock:
                    self.clients[client_id] = client_handler
                
                # 启动客户端处理
                client_handler.start()
                
                # 清理已断开连接
                self._cleanup_clients()
                
            except socket.timeout:
                continue
            except OSError as e:
                if self.running:
                    self.logger.error(f"接受连接时出错: {e}")
                break
            except Exception as e:
                self.logger.error(f"服务器循环异常: {e}")
                if self.running:
                    time.sleep(1)
    
    def _cleanup_clients(self):
        """清理已断开连接的客户端"""
        with self.client_lock:
            disconnected = []
            for client_id, handler in self.clients.items():
                if not handler.thread.is_alive():
                    disconnected.append(client_id)
            
            for client_id in disconnected:
                del self.clients[client_id]
            
            self.stats["current_connections"] = len(self.clients)
            
            if disconnected:
                self.logger.debug(f"清理了 {len(disconnected)} 个断开连接的客户端")
    
    def broadcast(self, message: Any) -> int:
        """
        广播消息给所有客户端
        
        Args:
            message: 要广播的消息
            
        Returns:
            int: 成功发送的客户端数量
        """
        success_count = 0
        
        with self.client_lock:
            for handler in self.clients.values():
                if handler.send(message):
                    success_count += 1
        
        self.logger.info(f"广播消息给 {success_count}/{len(self.clients)} 个客户端")
        return success_count
    
    def get_server_stats(self) -> Dict:
        """获取服务器统计信息"""
        stats = self.stats.copy()
        stats["uptime"] = time.time() - stats["start_time"]
        stats["client_count"] = len(self.clients)
        
        # 客户端详细统计
        client_stats = []
        with self.client_lock:
            for handler in self.clients.values():
                client_stats.append(handler.get_stats())
        
        stats["clients"] = client_stats
        return stats
    
    def get_client_count(self) -> int:
        """获取当前客户端连接数"""
        return len(self.clients)