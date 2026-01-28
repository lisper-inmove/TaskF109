# widgets/button_panel.py
from common import Commands
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class ButtonPanel(QWidget):
    """自定义按钮面板"""

    def __init__(self, button_callback, names):
        super().__init__()
        self.button_callback = button_callback
        self.names = names
        self.init_ui()

    def __on_btn_click(self, checked, idx):
        name = self.names[idx]
        cmd = list(Commands)[idx]
        self.button_callback(cmd, name=name)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # 第二行：按钮
        row2_widget = QWidget()
        row2_layout = QHBoxLayout()
        row2_layout.setContentsMargins(0, 10, 0, 10)

        self.buttons_row2 = []
        for i in range(len(self.names)):
            btn = QPushButton(f"Set {chr(65+i)}")
            btn.clicked.connect(
                lambda checked, idx=i: self.__on_btn_click(checked, idx))
            row2_layout.addWidget(btn)
            self.buttons_row2.append(btn)

        row2_widget.setLayout(row2_layout)
        layout.addWidget(row2_widget)

        # 第三行：按钮
        row3_widget = QWidget()
        row3_layout = QHBoxLayout()
        row3_layout.setContentsMargins(0, 10, 0, 10)

        self.buttons_row3 = []

        # 同时下发到所有板卡
        btn = QPushButton("Set All")
        btn.clicked.connect(
            lambda checked, idx=i: self.button_callback(Commands.SetAll))
        row3_layout.addWidget(btn)
        self.buttons_row3.append(btn)

        # 速度测试
        btn = QPushButton("Speed Test")
        btn.clicked.connect(
            lambda checked, idx=i: self.button_callback(Commands.SpeedTest))
        row3_layout.addWidget(btn)
        self.buttons_row3.append(btn)

        row3_widget.setLayout(row3_layout)
        layout.addWidget(row3_widget)

        self.setLayout(layout)

    def get_all_buttons(self):
        """获取所有按钮"""
        return self.buttons_row2 + self.buttons_row3
