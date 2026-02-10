from log_config import main_logger as logger
from PyQt5.QtWidgets import QGroupBox, QLineEdit, QPushButton, QVBoxLayout


class SectionWidget(QGroupBox):
    """自定义部分部件"""

    def __init__(self, title, connect_cb, disconnect_cb):
        super().__init__(title)
        self.__conn_cb = connect_cb
        self.__disconn_cb = disconnect_cb
        self.__base_title = title
        self.__conn_btn = QPushButton("Connect")
        self.__disconn_btn = QPushButton("Disconnect")
        self.__input1 = QLineEdit()
        self.__input2 = QLineEdit()
        self.init_ui()
        self.update_title(False)

    def init_ui(self):
        layout = QVBoxLayout()

        self.__input1 = QLineEdit()
        self.__input1.setPlaceholderText("Ip")
        layout.addWidget(self.__input1)

        self.__input2 = QLineEdit()
        self.__input2.setPlaceholderText("Port")
        layout.addWidget(self.__input2)

        self.__conn_btn.clicked.connect(self.__on_connect)
        layout.addWidget(self.__conn_btn)

        self.__disconn_btn = QPushButton("Disconnect")
        self.__disconn_btn.clicked.connect(self.__on_disconnect)
        layout.addWidget(self.__disconn_btn)

        layout.addSpacing(10)
        layout.addStretch(1)

        self.setLayout(layout)

    def update_title(self, connected):
        """更新标题显示状态"""
        status = "Connected" if connected else "Not Connected"
        self.setTitle(f"{self.__base_title} [{status}]")

    # ================= 按钮事件 =================
    def __on_connect(self):
        """连接"""
        ip = self.__input1.text()
        port = self.__input2.text()
        try:
            port = int(port)
        except ValueError as ex:
            logger.error(f"Invalid port number: {port}")
            raise ex

        if self.__conn_cb:
            ret = self.__conn_cb(ip, port, self.__base_title)
            self.update_title(ret)

    def __on_disconnect(self):
        """断连"""
        if self.__disconn_cb:
            ret = self.__disconn_cb(self.__base_title)
            self.update_title(ret)
