from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QTextEdit


class QtLogEmitter(QObject):
    """用于跨线程发送日志到UI"""
    log_signal = pyqtSignal(str)


class LogWidget(QTextEdit):
    """日志显示窗口"""

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMinimumWidth(640)
        self.setPlaceholderText("Operation logs...")
        self.setLineWrapMode(QTextEdit.NoWrap)

        # 信号发射器
        self.emitter = QtLogEmitter()
        self.emitter.log_signal.connect(self.append_log)

    def append_log(self, text: str):
        """追加日志（在主线程执行）"""
        self.append(text)
        # 自动滚动到底部
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def write(self, text: str):
        """供日志系统调用"""
        self.emitter.log_signal.emit(text)
