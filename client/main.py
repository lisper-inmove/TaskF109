import os
import sys
import traceback
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMessageBox

from enhanced_window import EnhancedWindow
from log_config import main_logger as logger


def config():
    if os.environ.get('VOLTAGE_MIN') is None:
        os.environ['VOLTAGE_MIN'] = '10'
    if os.environ.get("VOLTAGE_MAX") is None:
        os.environ['VOLTAGE_MAX'] = '20000'
    if os.environ.get("PROTOCOL_TYPE") is None:
        os.environ["PROTOCOL_TYPE"] = "UDP"


def exception_hook(exc_type, exc_value, exc_traceback):
    """
    全局异常捕获：不让程序退出，而是弹窗提示
    """
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(
        traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.info(error_msg)
    QMessageBox.critical(None, "程序异常", f"发生未处理异常：\n\n{exc_value}")


def main():
    config()
    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    window = EnhancedWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
