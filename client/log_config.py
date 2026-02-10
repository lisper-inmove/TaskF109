import sys
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
        self._main_logger.add(
            widget.write,
            format=panel_log_format,
            enqueue=True,
        )


main_logger = LoggerFactory().get_main_logger()
heartbeat_logger = LoggerFactory().get_heartbeat_logger()
