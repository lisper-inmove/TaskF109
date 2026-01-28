# main.py
import sys
from PyQt5.QtWidgets import QApplication
from basic_window import MainWindow
from enhanced_window import EnhancedWindow

def main():
    app = QApplication(sys.argv)
    
    # 选择要使用的窗口版本
    use_enhanced = True  # 切换这里选择版本
    
    if use_enhanced:
        window = EnhancedWindow()
    else:
        window = MainWindow()
    
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()