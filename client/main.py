# main.py
import sys
from datetime import datetime

from loguru import logger
from PyQt5.QtWidgets import QApplication

from enhanced_window import EnhancedWindow


# 移除默认配置
def config_logger():
    logger.remove()

    # 1. 配置终端输出（控制台）
    logger.add(
        sys.stderr,
        format=
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
        backtrace=True,
        diagnose=True)

    # 2. 配置文件输出（带轮转）
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",  # 按日期分割文件
        rotation="200 MB",  # 单个文件最大200MB
        retention="30 days",  # 保留30天
        compression="zip",  # 可选：压缩旧日志
        format=
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="DEBUG",  # 文件日志级别
        encoding="utf-8",
        enqueue=True,  # 多进程安全
        backtrace=True,
        diagnose=True)

    # 3. 可选：特定错误日志单独记录
    logger.add(
        "logs/error_{time:YYYY-MM-DD}.log",
        rotation="200 MB",
        retention="30 days",
        format=
        "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="ERROR",
        encoding="utf-8",
        enqueue=True)


def main():
    config_logger()
    app = QApplication(sys.argv)
    window = EnhancedWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
