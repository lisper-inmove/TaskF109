# client_handler.py
import socket
import threading
import time
from typing import Optional, Callable, Any
from protocol import ByteStreamProtocol
from utils.logger import setup_logger

class ClientHandler:
    """客户端连接处理器"""
    
    def __init__(self, client_socket: socket.socket, 
                 client_address: tuple,
                 protocol: ByteStreamProtocol,
                 on_message: Optional[Callable] = None,
                 timeout: int = 30):
        """
        初始化客户端处理器
        
        Args:
            client_socket: 客户端套接字
            client_address: 客户端地址 (ip, port)
            protocol: 协议处理器
            on_message: 消息处理回调函数
            timeout: 超时时间（秒）
        """
        self.client_socket = client_socket
        self.client_address = client_address
        self.protocol = protocol
        self.on_message = on_message
        self.timeout = timeout
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        # 设置套接字超时
        self.client_socket.settimeout(timeout)
        
        # 创建日志记录器
        self.logger = setup_logger(f"client_{client_address[0]}:{client_address[1]}")
        
        # 统计信息
        self.stats = {
            "bytes_received": 0,
            "bytes_sent": 0,
            "messages_received": 0,
            "messages_sent": 0,
            "connected_at": time.time(),
            "last_active": time.time()
        }
    
    def start(self):
        """启动客户端处理线程"""
        self.running = True
        self.thread = threading.Thread(target=self._handle_client, daemon=True)
        self.thread.start()
        self.logger.info(f"客户端连接处理器已启动")
    
    def stop(self):
        """停止客户端处理"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        self._close_connection()
        self.logger.info(f"客户端连接处理器已停止")
    
    def _handle_client(self):
        """处理客户端连接"""
        try:
            self.logger.info(f"客户端已连接: {self.client_address}")
            
            while self.running:
                try:
                    # 接收数据
                    data = self.client_socket.recv(4096)
                    
                    if not data:
                        self.logger.info("客户端断开连接")
                        break
                    
                    # 更新统计信息
                    self.stats["bytes_received"] += len(data)
                    self.stats["last_active"] = time.time()
                    
                    # 处理数据
                    self._process_data(data)
                    
                except socket.timeout:
                    # 超时检查
                    if time.time() - self.stats["last_active"] > self.timeout:
                        self.logger.warning("连接超时")
                        break
                    continue
                    
                except ConnectionResetError:
                    self.logger.warning("客户端强制关闭连接")
                    break
                    
                except Exception as e:
                    self.logger.error(f"处理数据时出错: {e}")
                    break
                    
        except Exception as e:
            self.logger.error(f"客户端处理异常: {e}")
            
        finally:
            self._close_connection()
    
    def _process_data(self, data: bytes):
        """处理接收到的数据"""
        try:
            result = self.protocol.unpack(data)
            
            if result:
                message, _ = result
                self.stats["messages_received"] += 1
                
                self.logger.info(f"收到消息: {message}")
                
                # 调用消息处理回调
                if self.on_message:
                    response = self.on_message(message, self.client_address)
                    self.send(response)
                else:
                    # 默认响应
                    default_response = self.protocol.create_response(
                        success=True,
                        message="消息已接收",
                        data={"received_message": message}
                    )
                    self.send(default_response)
        except Exception as e:
            self.logger.error(f"解析数据时出错: {e}")
            error_response = self.protocol.create_response(
                success=False,
                message=f"数据处理错误: {e}"
            )
            self.send(error_response)
    
    def send(self, data: Any) -> bool:
        """
        发送数据到客户端
        
        Args:
            data: 要发送的数据
            
        Returns:
            bool: 是否发送成功
        """
        try:
            packed_data = self.protocol.pack(data)
            self.client_socket.sendall(packed_data)
            
            # 更新统计信息
            self.stats["bytes_sent"] += len(packed_data)
            self.stats["messages_sent"] += 1
            self.stats["last_active"] = time.time()
            
            self.logger.debug(f"发送消息: {data}")
            return True
            
        except Exception as e:
            self.logger.error(f"发送数据失败: {e}")
            return False
    
    def _close_connection(self):
        """关闭连接"""
        try:
            self.client_socket.close()
            self.logger.info(f"连接已关闭")
            
            # 打印统计信息
            duration = time.time() - self.stats["connected_at"]
            self.logger.info(f"连接统计: "
                           f"接收={self.stats['bytes_received']}字节/{self.stats['messages_received']}消息, "
                           f"发送={self.stats['bytes_sent']}字节/{self.stats['messages_sent']}消息, "
                           f"持续时间={duration:.2f}秒")
        except:
            pass
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        stats = self.stats.copy()
        stats["duration"] = time.time() - stats["connected_at"]
        stats["client_address"] = self.client_address
        return stats