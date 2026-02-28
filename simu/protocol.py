# protocol.py
import json
import struct
from datetime import datetime
from typing import Any, Dict, Optional, Tuple


class ByteStreamProtocol:
    """
    字节流协议处理器
    协议格式: [4字节长度][数据]
    """

    def __init__(self, header_size: int = 4, encoding: str = 'utf-8'):
        """
        初始化协议处理器

        Args:
            header_size: 头部长度（字节）
            encoding: 字符串编码
        """
        self.header_size = header_size
        self.encoding = encoding
        self.buffer = bytearray()

    def pack(self, data: Any) -> bytes:
        """
        打包数据为字节流

        Args:
            data: 要发送的数据

        Returns:
            bytes: 打包后的字节流
        """
        if isinstance(data, str):
            data_bytes = data.encode(self.encoding)
        elif isinstance(data, (dict, list)):
            data_bytes = json.dumps(data,
                                    ensure_ascii=False).encode(self.encoding)
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            data_bytes = str(data).encode(self.encoding)

        # 添加长度头
        header = struct.pack('!I', len(data_bytes))
        return header + data_bytes

    def unpack(self, data: bytes) -> Optional[Tuple[Any, bytes]]:
        """
        从字节流解包数据

        Args:
            data: 接收到的字节流

        Returns:
            Optional[Tuple[Any, bytes]]: (解包的数据, 剩余的字节流) 或 None
        """
        self.buffer.extend(data)
        import pdb
        pdb.set_trace()

        # 检查是否有足够的数据读取头部
        if len(self.buffer) < self.header_size:
            return None

        # 读取数据长度
        data_length = struct.unpack('!I', self.buffer[:self.header_size])[0]

        # 检查是否有完整的数据包
        if len(self.buffer) < self.header_size + data_length:
            return None

        # 提取数据部分
        data_bytes = self.buffer[self.header_size:self.header_size +
                                 data_length]

        # 从缓冲区移除已处理的数据
        del self.buffer[:self.header_size + data_length]
        # 尝试解码数据
        try:
            # 尝试作为JSON解码
            decoded_data = json.loads(data_bytes.decode(self.encoding))
        except json.JSONDecodeError:
            try:
                # 尝试作为字符串解码
                decoded_data = data_bytes.decode(self.encoding)
            except UnicodeDecodeError:
                # 保持为字节
                decoded_data = data_bytes

        return decoded_data, bytes(self.buffer)

    def clear_buffer(self):
        """清空缓冲区"""
        self.buffer.clear()

    def create_response(self,
                        success: bool,
                        message: str = "",
                        data: Any = None) -> Dict:
        """
        创建标准响应

        Args:
            success: 是否成功
            message: 消息文本
            data: 附加数据

        Returns:
            Dict: 响应字典
        """
        return {
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
