import os

import pandas as pd
from common import ButtonNames, Commands, DeviceEnums
from log_config import main_logger as logger
from pandas import DataFrame
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QPushButton,
                             QSizePolicy, QSpinBox, QVBoxLayout, QWidget)


class ButtonPanel(QWidget):
    """自定义按钮面板"""

    def __init__(self, button_callback):
        super().__init__()
        self.button_callback = button_callback
        self.__buttons = []
        self.__voltage_input = QSpinBox()
        self.__layout = QVBoxLayout()
        self.__layout.setContentsMargins(0, 0, 0, 0)
        v_min = os.environ.get('VOLTAGE_MIN')
        v_max = os.environ.get('VOLTAGE_MAX')
        self.__voltage_min = int(v_min)
        self.__voltage_max = int(v_max)
        self.__df: DataFrame = None
        self.__file_label = QLabel("File Not Selected")
        self.__file_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.__file_label.setWordWrap(True)
        self.__file_label.setSizePolicy(QSizePolicy.Expanding,
                                        QSizePolicy.Fixed)
        # 状态提示
        self.__status_label = QLabel("")
        self.__status_label.setAlignment(Qt.AlignCenter)
        self.__status_label.setStyleSheet("color: red; font-weight: bold;")
        self.__status_label.hide()
        self.setLayout(self.__layout)
        self.__layout.addWidget(self.__status_label)

    @property
    def voltage(self):
        return self.__voltage_input.value()

    @property
    def csv_data(self):
        if self.__df is None:
            return None
        return self.__df

    def __on_btn_click(self, _, name):
        self.set_busy(True)
        cmd = Commands.SetVoltage
        logger.info(f"on btn click: {name} {cmd}")
        self.button_callback(cmd, name=name)

    def set_busy(self, busy: bool):
        """控制界面忙状态"""
        for btn in self.__buttons:
            btn.setEnabled(not busy)

        self.__voltage_input.setEnabled(not busy)

        if busy:
            self.__status_label.setText("执行中...")
            self.__status_label.show()
        else:
            self.__status_label.hide()

    def build(self):
        pass

    def add_voltage_area(self):
        """添加电压输入框.

        Args:
            main_layout: 父布局
        Returns:
            None
        """
        input_layout = QHBoxLayout()
        self.__voltage_input.setRange(0, self.__voltage_max)
        self.__voltage_input.setValue(self.__voltage_min)
        self.__voltage_input.setMinimumHeight(40)
        self.__voltage_input.setSizePolicy(QSizePolicy.Expanding,
                                           QSizePolicy.Fixed)

        unit_label = QLabel("mV")
        unit_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        unit_label.setMinimumHeight(40)
        unit_label.setFixedWidth(30)

        input_layout.addWidget(self.__voltage_input, 1)
        input_layout.addWidget(unit_label, 0)
        self.__layout.addLayout(input_layout)

        row2_widget = QWidget()
        row2_layout = QHBoxLayout()
        row2_layout.setContentsMargins(0, 10, 0, 10)

        self.__add_a_set_button(ButtonNames.SetA, row2_layout)
        self.__add_a_set_button(ButtonNames.SetB, row2_layout)
        self.__add_a_set_button(ButtonNames.SetC, row2_layout)
        self.__add_a_set_button(ButtonNames.SetD, row2_layout)

        row2_widget.setLayout(row2_layout)
        self.__layout.addWidget(row2_widget)

        self.__add_a_set_button(ButtonNames.SetAll, row2_layout)

    def __add_a_set_button(self, name, layout):
        btn = QPushButton(name)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;  /* 正常绿色 */
                color: white;
                border-radius: 5px;
            }
            QPushButton:disabled {
                background-color: #A0A0A0;  /* 灰色禁用 */
                color: #555555;
            }
        """)
        btn.clicked.connect(lambda clicked: self.__on_btn_click(clicked, name))
        layout.addWidget(btn)
        self.__buttons.append(btn)

    def add_speed_test_area(self):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 10, 0, 10)

        load_btn = QPushButton(ButtonNames.LoadCSV)
        load_btn.clicked.connect(self.__on_load_csv)
        layout.addWidget(load_btn, 1)

        layout.addWidget(self.__file_label, 1)

        btn = QPushButton(ButtonNames.SpeedTest)
        btn.clicked.connect(
            lambda checked: self.button_callback(Commands.SpeedTest))
        layout.addWidget(btn, 1)

        widget.setLayout(layout)
        self.__layout.addWidget(widget)

    def __on_load_csv(self):
        filename, _ = QFileDialog.getOpenFileName(
            None,
            "选择CSV文件",
            "",
            "CSV文件 (*.csv);;所有文件 (*.*)",
        )
        if not filename:
            return
        self.__df = pd.read_csv(filename)
        columns = list(DeviceEnums)
        if self.__df.columns.tolist() != columns:
            raise ValueError(f"CSV文件列名必须为: {columns}")
        self.__file_label.setText(os.path.basename(filename))
