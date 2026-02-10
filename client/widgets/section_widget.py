from log_config import main_logger as logger
from PyQt5.QtWidgets import QGroupBox, QLineEdit, QPushButton, QVBoxLayout


class SectionWidget(QGroupBox):
    """自定义部分部件"""

    def __init__(self, title, connect_cb, disconnect_cb):
        super().__init__(title)
        self.connect_cb = connect_cb
        self.disconnect_cb = disconnect_cb
        self.base_title = title
        self.init_ui()
        self.update_title(False)

    def init_ui(self):
        layout = QVBoxLayout()

        self.input1 = QLineEdit()
        self.input1.setPlaceholderText("Ip")
        layout.addWidget(self.input1)

        self.input2 = QLineEdit()
        self.input2.setPlaceholderText("Port")
        layout.addWidget(self.input2)

        # Connect
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.on_connect_button_clicked)
        layout.addWidget(self.connect_button)

        # ReConnect
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(
            self.on_disconnect_button_clicked)
        layout.addWidget(self.disconnect_button)

        layout.addSpacing(10)
        layout.addStretch(1)

        self.setLayout(layout)

    def update_title(self, connected):
        """更新标题显示状态"""
        status = "Connected" if connected else "Not Connected"
        self.setTitle(f"{self.base_title} [{status}]")

    # ================= 按钮事件 =================
    def on_connect_button_clicked(self):
        """连接"""
        ip = self.input1.text()
        try:
            port = int(self.input2.text())
        except ValueError as ex:
            logger.error(f"Invalid port number: {self.input2.text()}")
            raise ex

        if self.connect_cb:
            ret = self.connect_cb(ip, port, self.base_title)
            self.update_title(ret)

    def on_disconnect_button_clicked(self):
        """断连"""
        if self.disconnect_cb:
            ret = self.disconnect_cb(self.base_title)
            self.update_title(ret)

    # ================= 输入接口 =================
    def get_inputs(self):
        return self.input1.text(), self.input2.text()

    def set_inputs(self, text1, text2):
        self.input1.setText(text1)
        self.input2.setText(text2)
