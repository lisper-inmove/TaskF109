import sys
import traceback
from pathlib import Path
from threading import Lock

from loguru import logger

log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{file.name}:{line}</cyan> | <cyan>{function}</cyan> - {message}"

panel_log_format = "<green>{time:HH:mm:ss}</green> | {message}"


class LoggerFactory:
    _instance = None
    _lock = Lock()

    _initialized = False
    _main_logger = None
    _heartbeat_logger = None
    _exception_hook_set = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def _init_loggers(self):
        if self._initialized:
            return

        # 清掉 loguru 默认的 stdout logger
        logger.remove()

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # ---------- main logger sinks ----------
        logger.add(
            sys.stdout,
            level="INFO",
            filter=lambda r: r["extra"].get("logger_name") == "main",
            format=log_format,
        )

        logger.add(
            log_dir / "main.log",
            level="INFO",
            rotation="10 MB",
            retention="7 days",
            filter=lambda r: r["extra"].get("logger_name") == "main",
            format=log_format,
        )

        # ---------- heartbeat logger sinks ----------
        logger.add(
            log_dir / "heartbeat.log",
            level="INFO",
            rotation="5 MB",
            retention="3 days",
            filter=lambda r: r["extra"].get("logger_name") == "heartbeat",
            format=log_format,
        )

        # bind 出两个逻辑 logger
        self._main_logger = logger.bind(logger_name="main")
        self._heartbeat_logger = logger.bind(logger_name="heartbeat")

        self._initialized = True

    def get_main_logger(self):
        self._init_loggers()
        return self._main_logger

    def get_heartbeat_logger(self):
        self._init_loggers()
        return self._heartbeat_logger

    def add_qt_log_sink(self, widget):
        """添加 Qt 控件作为日志输出目标"""

        def qt_sink(message):
            # message 是 loguru 的 Message 对象
            # 使用 str(message) 获取格式化后的字符串
            widget.write(str(message))

        self._main_logger.add(
            qt_sink,
            format=panel_log_format,
            enqueue=True,
        )

    def setup_exception_hook(self):
        """设置全局异常处理钩子，用于捕获未处理的异常"""
        if self._exception_hook_set:
            return

        self._init_loggers()

        def exception_hook(exc_type, exc_value, exc_tb):
            """安全的全局异常处理函数"""
            try:
                # 格式化异常信息
                formatted_exception = ''.join(
                    traceback.format_exception(exc_type, exc_value, exc_tb))

                # 使用 opt 方法避免调用栈深度问题
                # 先尝试使用 main_logger
                try:
                    self._main_logger.opt(depth=0, exception=False).error(
                        f"程序发生未捕获的异常:\n{formatted_exception}")
                except Exception:
                    # 如果 main_logger 失败，直接使用 root logger
                    logger.opt(depth=0, exception=False).error(
                        f"程序发生未捕获的异常:\n{formatted_exception}")

            except Exception as log_error:
                # 如果日志记录也失败，至少打印到控制台
                print(f"日志记录失败: {log_error}", file=sys.stderr)
                print(formatted_exception, file=sys.stderr)

        # 替换默认的异常钩子
        sys.excepthook = exception_hook
        self._exception_hook_set = True

        # 可选：同时设置线程异常钩子
        try:
            import threading
            threading.excepthook = lambda args: exception_hook(
                args.exc_type, args.exc_value, args.exc_tb)
        except Exception:
            pass

    def safe_log_exception(self, exc_info=None, message="发生异常"):
        """安全地记录异常信息"""
        try:
            if exc_info is None:
                exc_info = sys.exc_info()

            if exc_info[0] is not None:
                formatted_exception = ''.join(
                    traceback.format_exception(*exc_info))
                self._main_logger.opt(depth=1, exception=False).error(
                    f"{message}:\n{formatted_exception}")
        except Exception:
            # 降级处理
            print(f"异常记录失败: {message}", file=sys.stderr)

    def get_exception_logger(self):
        """获取用于异常处理的 logger（禁用调用栈信息）"""
        self._init_loggers()
        return self._main_logger.opt(depth=0)


# 创建全局实例
logger_factory = LoggerFactory()
main_logger = logger_factory.get_main_logger()
heartbeat_logger = logger_factory.get_heartbeat_logger()
