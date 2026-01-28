# widgets/button_panel.py
from PyQt5.QtWidgets import *

class ButtonPanel(QWidget):
    """自定义按钮面板"""
    def __init__(self, button_callback):
        super().__init__()
        self.button_callback = button_callback
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 第二行：按钮
        row2_widget = QWidget()
        row2_layout = QHBoxLayout()
        row2_layout.setContentsMargins(0, 10, 0, 10)
        
        self.buttons_row2 = []
        for i in range(3):
            btn = QPushButton(f"操作 {i+1}")
            btn.clicked.connect(lambda checked, idx=i: 
                              self.button_callback(idx, "row2"))
            row2_layout.addWidget(btn)
            self.buttons_row2.append(btn)
        
        row2_widget.setLayout(row2_layout)
        layout.addWidget(row2_widget)
        
        # 第三行：按钮
        row3_widget = QWidget()
        row3_layout = QHBoxLayout()
        row3_layout.setContentsMargins(0, 10, 0, 10)
        
        self.buttons_row3 = []
        for i in range(3):
            btn = QPushButton(f"功能 {i+4}")
            btn.clicked.connect(lambda checked, idx=i: 
                              self.button_callback(idx+3, "row3"))
            row3_layout.addWidget(btn)
            self.buttons_row3.append(btn)
        
        row3_widget.setLayout(row3_layout)
        layout.addWidget(row3_widget)
        
        self.setLayout(layout)
    
    def get_all_buttons(self):
        """获取所有按钮"""
        return self.buttons_row2 + self.buttons_row3