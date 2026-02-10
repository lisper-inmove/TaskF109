from PyQt5.QtCore import Qt, QThreadPool, pyqtSlot
from PyQt5.QtWidgets import (QAction, QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QMessageBox, QSizePolicy, QSpinBox,
                             QVBoxLayout, QWidget)

from common import BtnToDeviceMap, ButtonNames, Commands, DeviceEnums
from controller import Controller
from heartbeat_thread import HeartbeatThread
from log_config import LoggerFactory
from log_config import main_logger as logger
from task import Task
from timing import simple_timer
from utils.styles import get_enhanced_styles
from widgets.button_panel import ButtonPanel
from widgets.log_widget import LogWidget
from widgets.section_widget import SectionWidget
from worker import BatchWorker


class EnhancedWindow(QMainWindow):
    """增强版本，添加更多功能"""

    def __init__(self):
        super().__init__()
        # 创建4个部分，使用自定义部件
        self.sections = []
        self.controller = Controller()
        self.thread_pool = QThreadPool()
        self.heartbeat_thread = HeartbeatThread()
        self.heartbeat_thread.start()
        self.thread_pool.setMaxThreadCount(8)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('上位机程序')
        self.setGeometry(100, 100, 1600, 700)

        # 创建中心窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # ========== 板卡区域 ========
        self.__init_boards(left_layout)
        # =========== 指令发送区域 ===========
        self.__init_control_panel(left_layout)

        main_layout.addWidget(left_widget, 3)

        self.log_widget = LogWidget()
        main_layout.addWidget(self.log_widget, 1)
        LoggerFactory().add_qt_log_sink(self.log_widget)

        # 设置样式
        self.setStyleSheet(get_enhanced_styles())

    def __init_boards(self, main):
        """初始化板卡列表部分."""
        a_container = QFrame()
        a_container.setFrameStyle(QFrame.Box | QFrame.Raised)
        a_layout = QHBoxLayout()

        for name in DeviceEnums:
            section = SectionWidget(
                name,
                self.__connect_device,
                self.__disconnect,
            )
            a_layout.addWidget(section)
            self.sections.append(section)

        a_container.setLayout(a_layout)
        main.addWidget(a_container, 3)
        logger.info("Create 4 device sections in area A.")

    def __init_control_panel(self, main):
        """初始化控制面板.

        Args:
            main: 父布局
        Returns:
            None
        """
        b_container = QFrame()
        b_container.setFrameStyle(QFrame.Box | QFrame.Raised)

        # 外层：纵向布局
        b_layout = QVBoxLayout()

        # ---------- 按钮面板 ----------
        self.button_panel = ButtonPanel(self.__on_send_cmd)
        self.button_panel.add_voltage_area()
        self.button_panel.add_speed_test_area()
        b_layout.addWidget(self.button_panel)

        b_layout.addStretch(1)

        b_container.setLayout(b_layout)
        main.addWidget(b_container, 2)

        logger.info("Create control panel in area B.")

    def __disconnect(self, name):
        """断开连接事件"""
        device = self.controller.get_device(name)
        if device:
            self.heartbeat_thread.remove_device(device)
            device.disconnect()
            self.controller.remove_device(name)
            logger.info(f"Device disconnected: {name}")
        else:
            logger.info(f"Device not connected: {name}")

    def __connect_device(self, ip, port, name):
        """连接事件"""
        self.controller.add_device(ip, port, name)
        device = self.controller.get_device(name)
        if device is None:
            raise ValueError(f"{name} is not connected")
        device.connect()
        self.heartbeat_thread.add_device(device)
        return device.connected

    @simple_timer
    def __on_send_cmd(self, cmd, name=None):
        """指令事件"""
        logger.info(f"Send {cmd} for device: {name}")
        if cmd in Commands.SetVoltage:
            if name == ButtonNames.SetAll:
                self.__handle_set_all_async()
            else:
                task = self.__create_voltage_set_task(BtnToDeviceMap.get(name))
                self.__send_single_device_task(task)
        elif cmd == Commands.SpeedTest:
            self.__handle_speed_test_async()
        else:
            raise ValueError(f"Unknown command: {cmd}")

    def __data(self):
        try:
            voltage = self.button_panel.voltage
        except Exception as ex:
            logger.error(f"Invalid voltage input: {ex}")
            raise ex
        return voltage

    def __create_speed_test_task(self, device_name, data):
        return Task(Commands.SpeedTest, device_name, data)

    def __create_voltage_set_task(self, device_name):
        return Task(Commands.SetVoltage, device_name, self.__data())

    def __handle_speed_test_async(self):
        tasks = []
        df = self.button_panel.csv_data
        if df is None:
            raise ValueError("No CSV data available for speed test.")
        names = list(DeviceEnums)
        for name in names:
            tasks.append(self.__create_speed_test_task(name, list(df[name])))
        worker = BatchWorker(self.__send_speed_test_task, tasks)
        self.thread_pool.start(worker)

    def __handle_set_all_async(self):
        """Set All"""
        tasks = []
        names = list(DeviceEnums)
        for name in names:
            tasks.append(self.__create_voltage_set_task(name))
        worker = BatchWorker(self.__send_single_device_task, tasks)
        self.thread_pool.start(worker)

    @simple_timer
    def __send_single_device_task(self, task: Task):
        """单个设备发送任务"""
        logger.info(
            f"Send {task.cmd} to {task.device_name} with data: {task.data}")
        device = self.controller.get_device(task.device_name)
        if device is None:
            self.button_panel.set_busy(False)
            logger.info(f"Device not connected: {task.device_name}")
            return (task.device_name, False,
                    f"{task.device_name} is not connected")
        device.send_set_voltage(task.data)
        self.button_panel.set_busy(False)
        return (task.device_name, True, None)

    @simple_timer
    def __send_speed_test_task(self, task: Task):
        """Speed Test"""
        device = self.controller.get_device(task.device_name)
        if device is None:
            self.button_panel.set_busy(False)
            logger.info(f"Device not connected: {task.device_name}")
            return (task.device_name, False,
                    f"{task.device_name} is not connected")
        device.send_multi_voltage(task.data)
        self.button_panel.set_busy(False)
        return (task.device_name, True, None)
