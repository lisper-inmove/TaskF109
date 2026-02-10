# utils/logger.py
import logging
import sys
from datetime import datetime
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""
    COLORS = {
        'DEBUG': '\033[94m',  # 蓝色
        'INFO': '\033[92m',  # 绿色
        'WARNING': '\033[93m',  # 黄色
        'ERROR': '\033[91m',  # 红色
        'CRITICAL': '\033[95m',  # 紫色
        'RESET': '\033[0m'  # 重置
    }

    def format(self, record):
        log_message = super().format(record)
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        return f"{color}{log_message}{self.COLORS['RESET']}"


def setup_logger(name: str = "tcp_server",
                 level: str = "INFO",
                 log_file: Optional[str] = None) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 记录器名称
        level: 日志级别
        log_file: 日志文件路径，为None则不写入文件

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # 清除已有的处理器
    logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    log_format = ('%(asctime)s - %(name)s - %(levelname)s '
                  '- [%(filename)s:%(lineno)d] - %(message)s')
    console_formatter = ColoredFormatter(log_format,
                                         datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 文件处理器（如果指定了文件）
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(log_format,
                                           datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger
