import json
import webbrowser

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from Daily_Fortune.DailyFortune import DailyFortuneWindow
import os
import sys
from utils import resource_path


class MorePage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 使用垂直布局作为主布局
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)  # 内容居中
        main_layout.setSpacing(40)  # 按钮间距

        # 创建按钮容器
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setAlignment(Qt.AlignCenter)
        buttons_layout.setSpacing(20)  # 按钮间距

        # 添加"今日运势"按钮
        fortune_button = self.create_button("今日运势", self.handle_fortune_click)
        buttons_layout.addWidget(fortune_button)

        # 添加"帮助文档"按钮
        help_button = self.create_button("帮助文档", self.open_help)
        buttons_layout.addWidget(help_button)

        # 添加"关于我们"按钮
        about_button = self.create_button("关于我们", self.open_about)
        buttons_layout.addWidget(about_button)

        # 添加"项目仓库"按钮
        repo_button = self.create_button("项目仓库", self.open_repository)
        buttons_layout.addWidget(repo_button)

        # 将按钮容器添加到主布局
        main_layout.addWidget(buttons_container)

        # 添加底部版权信息
        footer_label = QLabel("© 2025 不用Debug都队 NoDebug Team", self)
        footer_label.setStyleSheet("""
            QLabel {
                font-family: "微软雅黑";  /* 字体名称 */
                font-size: 17px;
                color: gray;
                margin-top: 50px;
            }
        """)
        footer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(footer_label)

        # 设置主布局
        self.setLayout(main_layout)

    def load_theme(self):
        """从 theme.json 中读取指定主题"""
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        THEME_FILE = os.path.join(self.base_path, "theme.json")
        try:
            if os.path.exists(THEME_FILE):
                with open(THEME_FILE, 'r', encoding='utf-8') as f:
                    themes = json.load(f)
                    return themes
            else:
                print("未找到 theme.json，使用默认配色")
                return {
                    "first": "#caf0f8",
                    "second": "#90e0ef",
                    "third": "#00b4d8",
                    "fourth": "#0077b6",
                    "background":"#045296"
                }
        except Exception as e:
            print(f"读取主题失败: {e}")
            return {
                "first": "#caf0f8",
                "second": "#90e0ef",
                "third": "#00b4d8",
                "fourth": "#0077b6",
                "background":"#045296"
            }

    def create_button(self, text, callback):
        """创建统一风格的按钮"""
        theme=self.load_theme()
        button = QPushButton(text, self)
        button.setFixedSize(200, 50)  # 固定按钮大小
        button.setStyleSheet(f"""
                QPushButton {{
                    font-family: "微软雅黑";  /* 字体名称 */
                    background-color: {theme["fourth"]};
                    color: white;
                    font-size: 18px;
                    font-weight: bold;
                    border-radius: 10px;
                    border: 4px solid {theme["second"]};
                }}
                QPushButton:hover {{
                    background-color: {theme["third"]};
                    border-color: {theme["second"]};
                }}
            """)
        button.clicked.connect(callback)
        return button

    def handle_fortune_click(self):
        if hasattr(self, 'fortune_window') and self.fortune_window.isVisible():
            return

        self.fortune_window = DailyFortuneWindow(self)
        self.fortune_window.exec_()

    def open_repository(self):
        """打开项目仓库链接"""
        repo_url = "https://git.nju.edu.cn/Benzoic/el-project-nodebug.git"
        QDesktopServices.openUrl(QUrl(repo_url))

    def open_about(self):
        remote_url = "https://wtynju.github.io/NoDebug/about.html"

        try:
            # 尝试打开远程网页
            if QDesktopServices.openUrl(QUrl(remote_url)):
                print("成功打开远程关于页面")
                return
            else:
                print("无法打开远程页面，尝试打开本地文件")

            # 获取项目根目录
            about_path = resource_path("docs/about.html")

            if not os.path.exists(about_path):
                raise FileNotFoundError(f"HTML文件不存在: {about_path}")

            if sys.platform == "win32":
                os.startfile(about_path)
            else:
                webbrowser.open(f"file://{about_path}")

        except Exception as e:
            print(f"打开关于页面失败: {str(e)}")

    def open_help(self):
        remote_url = "https://wtynju.github.io/NoDebug/help.html"

        try:
            # 尝试打开远程网页
            if QDesktopServices.openUrl(QUrl(remote_url)):
                print("成功打开远程帮助页面")
                return
            else:
                print("无法打开远程页面，尝试打开本地文件")

            # 获取项目根目录
            about_path = resource_path("docs/help.html")

            if not os.path.exists(about_path):
                raise FileNotFoundError(f"HTML文件不存在: {about_path}")

            if sys.platform == "win32":
                os.startfile(about_path)
            else:
                webbrowser.open(f"file://{about_path}")

        except Exception as e:
            print(f"打开关于页面失败: {str(e)}")