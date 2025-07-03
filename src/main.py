import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

from utils import resource_path

# 确保项目根目录在系统路径中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# 确保 src 目录在系统路径中
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

from panel import ControlPanel  # 从 panel.py 导入窗口类

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("model/icon.png")))
    panel = ControlPanel()  # 创建你的大面板
    sys.exit(app.exec_())   # 启动事件循环
