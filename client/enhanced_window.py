# enhanced_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from widgets.section_widget import SectionWidget
from widgets.button_panel import ButtonPanel
from utils.styles import get_enhanced_styles

class EnhancedWindow(QMainWindow):
    """增强版本，添加更多功能"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('增强版 PyQt 布局')
        self.setGeometry(100, 100, 900, 700)
        
        # 创建中心窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主垂直布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # ========== 板卡区域 ========
        self.__init_boards(main_layout)
        
        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # =========== 指令发送区域 ===========
        self.__init_control_panel(main_layout)
        
        # 添加菜单栏
        self.create_menu()
        
        # 设置样式
        self.setStyleSheet(get_enhanced_styles())

    def __init_boards(self, main):
        """初始化板卡列表部分."""
            # ========== 区域 A ==========
        a_container = QFrame()
        a_container.setFrameStyle(QFrame.Box | QFrame.Raised)
        a_layout = QHBoxLayout()
        
        # 创建4个部分，使用自定义部件
        self.sections = []
        for i in range(4):
            section = SectionWidget(f"部分 {chr(97+i)}", self.on_section_button_clicked)
            a_layout.addWidget(section)
            self.sections.append(section)
        
        a_container.setLayout(a_layout)
        main.addWidget(a_container, 3)

    def __init_control_panel(self, main):
                # ========== 区域 B ==========
        b_container = QFrame()
        b_container.setFrameStyle(QFrame.Box | QFrame.Raised)
        b_layout = QVBoxLayout()
        
        # 第一行：输入框
        self.b_input = QLineEdit()
        self.b_input.setPlaceholderText("请输入文本...")
        self.b_input.setMinimumHeight(40)
        b_layout.addWidget(self.b_input)
        
        # 使用自定义按钮面板
        self.button_panel = ButtonPanel(self.on_button_clicked)
        b_layout.addWidget(self.button_panel)
        
        b_container.setLayout(b_layout)
        main.addWidget(b_container, 2)

    def create_menu(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件')
        
        new_action = QAction('新建', self)
        open_action = QAction('打开', self)
        save_action = QAction('保存', self)
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助')
        about_action = QAction('关于', self)
        help_menu.addAction(about_action)
    
    def on_section_button_clicked(self, section_name):
        """A区域按钮点击事件"""
        QMessageBox.information(self, "按钮点击", 
                              f"点击了 {section_name} 的按钮")
    
    def on_button_clicked(self, button_index, row):
        """B区域按钮点击事件"""
        if row == "row2":
            QMessageBox.information(self, "按钮点击", 
                                  f"点击了第二行按钮 {button_index + 1}")
        else:
            QMessageBox.information(self, "按钮点击", 
                                  f"点击了第三行按钮 {button_index + 1}")