import os
import sys


def resource_path(relative_path):
    """获取资源的绝对路径。在开发时和打包后都可以正确运行"""
    try:
        # 如果程序被打包，PyInstaller会创建一个临时文件夹，路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 否则，使用当前文件的目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)