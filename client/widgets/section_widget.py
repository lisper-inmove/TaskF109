# widgets/section_widget.py
from PyQt5.QtWidgets import *

class SectionWidget(QGroupBox):
    """自定义部分部件"""
    def __init__(self, title, button_callback):
        super().__init__(title)
        self.button_callback = button_callback
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 输入框1
        self.input1 = QLineEdit()
        self.input1.setPlaceholderText("输入框 1")
        layout.addWidget(self.input1)
        
        # 输入框2
        self.input2 = QLineEdit()
        self.input2.setPlaceholderText("输入框 2")
        layout.addWidget(self.input2)
        
        # 按钮
        self.button = QPushButton("执 行")
        self.button.clicked.connect(self.on_button_clicked)
        layout.addWidget(self.button)
        
        # 添加一些间距和拉伸
        layout.addSpacing(10)
        layout.addStretch(1)
        
        self.setLayout(layout)
    
    def on_button_clicked(self):
        """按钮点击事件"""
        if self.button_callback:
            self.button_callback(self.title())
    
    def get_inputs(self):
        """获取输入内容"""
        return self.input1.text(), self.input2.text()
    
    def set_inputs(self, text1, text2):
        """设置输入内容"""
        self.input1.setText(text1)
        self.input2.setText(text2)