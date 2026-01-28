# basic_window.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('PyQt 布局示例')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中心窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主垂直布局（分为A和B两部分）
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # ========== 上部区域 A ==========
        # 创建A部分的容器
        a_container = QGroupBox("区域 A")
        a_layout = QHBoxLayout()  # 水平布局：a, b, c, d
        
        # 创建4个相同的部分（a, b, c, d）
        self.create_sections(a_layout)
        
        a_container.setLayout(a_layout)
        main_layout.addWidget(a_container, 3)  # 权重为3
        
        # ========== 下部区域 B ==========
        # 创建B部分的容器
        b_container = QGroupBox("区域 B")
        b_layout = QVBoxLayout()  # 垂直布局：三行
        
        # 第一行：一个输入框
        row1_layout = QHBoxLayout()
        b_input = QLineEdit()
        b_input.setPlaceholderText("B区域输入框")
        row1_layout.addWidget(b_input)
        b_layout.addLayout(row1_layout)
        
        # 第二行：3个按钮
        row2_layout = QHBoxLayout()
        buttons2 = ["按钮1", "按钮2", "按钮3"]
        for text in buttons2:
            btn = QPushButton(text)
            row2_layout.addWidget(btn)
        b_layout.addLayout(row2_layout)
        
        # 第三行：3个按钮
        row3_layout = QHBoxLayout()
        buttons3 = ["按钮4", "按钮5", "按钮6"]
        for text in buttons3:
            btn = QPushButton(text)
            row3_layout.addWidget(btn)
        b_layout.addLayout(row3_layout)
        
        b_container.setLayout(b_layout)
        main_layout.addWidget(b_container, 2)  # 权重为2
        
        # 添加样式
        self.apply_styles()
    
    def create_sections(self, layout):
        """创建4个相同的部分"""
        sections = ['a', 'b', 'c', 'd']
        
        for section_name in sections:
            # 创建每个部分的容器
            section_container = QGroupBox(f"部分 {section_name}")
            section_layout = QVBoxLayout()
            
            # 第一个输入框
            input1 = QLineEdit()
            input1.setPlaceholderText(f"{section_name} - 输入框1")
            section_layout.addWidget(input1)
            
            # 第二个输入框
            input2 = QLineEdit()
            input2.setPlaceholderText(f"{section_name} - 输入框2")
            section_layout.addWidget(input2)
            
            # 按钮
            btn = QPushButton(f"{section_name} 按钮")
            section_layout.addWidget(btn)
            
            # 添加拉伸因子，使内容靠上
            section_layout.addStretch(1)
            
            section_container.setLayout(section_layout)
            layout.addWidget(section_container)
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit {
                padding: 8px;
                font-size: 12px;
            }
        """)