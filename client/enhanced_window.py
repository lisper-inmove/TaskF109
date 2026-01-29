# enhanced_window.py
from loguru import logger
from PyQt5.QtCore import Qt, QThreadPool, pyqtSlot
from PyQt5.QtWidgets import (QAction, QFrame, QHBoxLayout, QLineEdit,
                             QMainWindow, QMessageBox, QVBoxLayout, QWidget)

from common import Commands, DeviceEnums
from controller import Controller
from timing import simple_timer
from utils.styles import get_enhanced_styles
from widgets.button_panel import ButtonPanel
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
        self.future_watchers = []
        self.thread_pool.setMaxThreadCount(4)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('上位机程序')
        self.setGeometry(100, 100, 900, 700)

        # 创建中心窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主垂直布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # ========== 板卡区域 ========
        self.__init_boards(main_layout)
        # =========== 指令发送区域 ===========
        self.__init_control_panel(main_layout)

        # 设置样式
        self.setStyleSheet(get_enhanced_styles())

    def __init_boards(self, main):
        """初始化板卡列表部分."""
        a_container = QFrame()
        a_container.setFrameStyle(QFrame.Box | QFrame.Raised)
        a_layout = QHBoxLayout()

        for name in DeviceEnums:
            section = SectionWidget(name, self.__connect_device)
            a_layout.addWidget(section)
            self.sections.append(section)

        a_container.setLayout(a_layout)
        main.addWidget(a_container, 3)
        logger.info("Create 4 device sections in area A.")

    def __init_control_panel(self, main):
        b_container = QFrame()
        b_container.setFrameStyle(QFrame.Box | QFrame.Raised)
        b_layout = QVBoxLayout()

        # 第一行：输入框
        self.b_input = QLineEdit()
        self.b_input.setPlaceholderText("请输入电压值(0.00 ~ 20.00)")
        self.b_input.setMinimumHeight(40)
        b_layout.addWidget(self.b_input)

        # 使用自定义按钮面板
        self.button_panel = ButtonPanel(
            self.__on_send_cmd,
            list(DeviceEnums),
        )
        b_layout.addWidget(self.button_panel)

        b_container.setLayout(b_layout)
        main.addWidget(b_container, 2)
        logger.info("Create control panel in area B.")

    def __connect_device(self, ip, port, name):
        """连接事件"""
        self.controller.add_device(ip, port, name)
        device = self.controller.get_device(name)
        if device is None:
            raise ValueError(f"{name} is not connected")
        device.connect()

    @simple_timer
    def __on_send_cmd(self, cmd, name=None):
        """指令事件"""
        logger.info(f"Send {cmd} for device: {name}")
        if cmd in [
                Commands.SetA,
                Commands.SetB,
                Commands.SetC,
                Commands.SetD,
        ]:
            self.__send_single_device_task({
                "cmd": cmd,
                "name": name,
                "data": "test",
            })
        elif cmd == Commands.SetAll:
            self.__handle_set_all_async()
        elif cmd == Commands.SpeedTest:
            pass
        else:
            raise ValueError(f"Unknown command: {cmd}")

    def __handle_set_all_async(self):
        """使用BatchWorker实现批量操作"""
        # 准备任务数据
        tasks = []
        commands = list(Commands)
        for index, name in enumerate(DeviceEnums):
            tasks.append({
                'cmd': commands[index],
                'name': name,
                'data': "Test"
            })

        # 创建批量工作器
        worker = BatchWorker(
            self.__send_single_device_task,
            tasks,
            self.__on_batch_complete,
        )

        self.thread_pool.start(worker)

    def __send_single_device_task(self, task_data):
        """单个设备发送任务"""
        cmd = task_data['cmd']
        name = task_data['name']
        data = task_data['data']
        logger.info(f"Send {cmd} to {name} with data: {data}")
        device = self.controller.get_device(name)
        if device is None:
            logger.info(f"Device not connected: {name}")
            return (name, False, f"{name} is not connected")
        device.send(data)
        return (name, True, None)

    def __on_batch_complete(self, results):
        """批量完成回调"""
        success_count = sum(1 for _, success, _ in results if success)
        total = len(results)

        logger.info(
            f"Batch operation completed: {success_count}/{total} successful")

        # 显示结果
        if success_count < total:
            failed_names = [
                name for name, success, _ in results if not success
            ]
            QMessageBox.warning(
                self, "Batch Operation", f"Success: {success_count}/{total}\n"
                f"Failed devices: {', '.join(failed_names)}")
        else:
            QMessageBox.information(
                self, "Success",
                f"All {total} devices completed successfully!")
