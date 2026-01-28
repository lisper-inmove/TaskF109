# utils/styles.py

def get_basic_styles():
    """获取基础样式"""
    return """
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
    """

def get_enhanced_styles():
    """获取增强样式"""
    return """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QFrame[frameShape="4"] {  /* Box */
            background-color: white;
            border: 2px solid #d0d0d0;
            border-radius: 5px;
            padding: 10px;
        }
        QLineEdit {
            border: 1px solid #ccc;
            border-radius: 3px;
            padding: 8px;
            font-size: 13px;
        }
        QLineEdit:focus {
            border: 2px solid #4CAF50;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            font-size: 13px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
    """