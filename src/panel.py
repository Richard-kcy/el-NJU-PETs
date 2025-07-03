import json
import os

from PyQt5.QtWidgets import QWidget, QPushButton, QStackedWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QColor, QPainter, QIcon, QPen, QBrush, QPainterPath, QPixmap
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QRectF, QEasingCurve
from schedule_page import SchedulePage
from setting_page import SettingPage
from more_page import MorePage
from controller import Controller
from utils import resource_path

class RoundedBackground(QWidget):
    def __init__(self,parent=None,theme=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(80, 10)
        self.theme=theme



    def paintEvent(self, event):
        if self.width() <= 0 or self.height() <= 0:
            return  # 安全防护：避免非法尺寸
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()

        # 将 QRect 转换为 QRectF
        rect = self.rect()
        rect_f = QRectF(rect)
        radius = min(self.width(), self.height()) / 2.0  # 使用 float 更精确


        path.addRoundedRect(rect_f, radius, radius)
        painter.fillPath(path, QBrush(QColor(self.theme["second"])))

    def move_to_center_of(self, widget, reference_widget=None):
        # 强制使用全局坐标映射
        global_pos = widget.mapToGlobal(QPoint(0, 0))  # 获取按钮在屏幕上的绝对位置
        panel_global_pos = self.window().mapToGlobal(QPoint(0, 0))  # 当前面板左上角的屏幕位置

        # 转换为面板内的相对坐标
        relative_x = global_pos.x() - panel_global_pos.x() + (widget.width() - self.width()) // 2
        relative_y = global_pos.y() - panel_global_pos.y() + (widget.height() - self.height()) // 2 + 20
        self.animate_move(relative_x, relative_y)

    def animate_move(self, x, y):
        """使用动画移动到目标位置"""
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(200)
        animation.setStartValue(self.pos())
        animation.setEndValue(QPoint(x, y))
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()
        animation.finished.connect(lambda: animation.deleteLater())


class ControlPanel(QWidget):

    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowIcon(QIcon(resource_path("model/png/pet.png")))
        self.controller = Controller(self)
        self.initUI()
        self.dragging = False  # 添加拖动状态标志

        # 加载背景图片
        self.background_pixmap = QPixmap(self.size())
        self.background_pixmap.fill(Qt.transparent)

        painter = QPainter(self.background_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 设置颜色 + 透明度
        color = QColor(self.theme["first"])
        color.setAlpha(216)  # 设置透明度值，0=全透明，255=不透明
        painter.fillRect(self.background_pixmap.rect(), QBrush(color))
        painter.end()

    def load_theme(self):
        """从 theme.json 中读取指定主题"""
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        THEME_FILE = os.path.join(self.base_path,"theme.json")
        try:
            if os.path.exists(THEME_FILE):
                with open(THEME_FILE, 'r', encoding='utf-8') as f:
                    themes = json.load(f)
                    return themes
            else:
                print("未找到 theme.json，使用默认配色")
                return {
                "first": "#E0FFDC",
                "second": "#39E6F4",
                "third": "#288BCF",
                "fourth": "#3C67DC",
                "background":"#045296"
                }
        except Exception as e:
            print(f"读取主题失败: {e}")
            return {
                "first": "#E0FFDC",
                "second": "#39E6F4",
                "third": "#288BCF",
                "fourth": "#3C67DC",
                "background":"#045296"
                }

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(800, 600)
        self.oldPos = self.pos()


        # 顶部按钮布局
        exit_btn_size = 50  # 退出按钮尺寸
        min_btn_size = 50
        main_btn_count = 4  # 主要按钮数量
        main_btn_width = (self.width() - exit_btn_size - min_btn_size) // main_btn_count  # 主要按钮宽度
        self.top_buttons = {}
        self.theme=self.load_theme()
        for i, name in enumerate(["启动", "日程", "设置", "更多"]):
            btn = QPushButton(name, self)
            btn.setGeometry(i * main_btn_width, 0, main_btn_width, 50)

            # 判断是否是第一个或最后一个按钮
            if i == 0:  # 第一个按钮 - 左上角圆角
                radius_style = """
                    border-top-left-radius: 15px;
                """
            else:
                radius_style = ""

            btn.setStyleSheet(f"""
                        QPushButton {{
                            font-family: "微软雅黑";  /* 字体名称 */
                            font-size: 18px;        /* 字号 */
                            font-weight: bold;      /* 加粗 */
                            color:{self.theme["first"]};
                            background-color: {self.theme["background"]};
                            border: none;  
                            {radius_style}
                        }}
                        QPushButton:hover {{
                            background-color: {self.theme["first"]};
                            color:{self.theme["background"]}
                        }}
                    """)
            self.top_buttons[name] = btn  # 保存按钮
            if name == "日程":
                btn.clicked.connect(self.show_schedule_page)
            elif name == "启动":
                btn.clicked.connect(self.show_main_page)
            elif name == "设置":
                btn.clicked.connect(self.show_setting_page)
            elif name == "更多":
                btn.clicked.connect(self.show_more_page)

            btn.mousePressEvent = lambda event, b=btn: self.buttonMousePressEvent(b, event)
            btn.mouseMoveEvent = lambda event, b=btn: self.buttonMouseMoveEvent(b, event)
            btn.mouseReleaseEvent = lambda event, b=btn: self.buttonMouseReleaseEvent(b, event)

        # 添加可移动的圆角背景
        self.rounded_background = RoundedBackground(self,  self.theme)
        self.rounded_background.move(47, 40)
        self.rounded_background.show()  # 初始显示

        # 创建最小化按钮.
        self.min_btn = QPushButton("—", self)
        self.min_btn.setGeometry(
            (main_btn_count * main_btn_width),  # 在退出按钮左边
            0,
            min_btn_size,
            min_btn_size
        )
        self.min_btn.setStyleSheet(f"""
                        QPushButton {{
                            font-family: "微软雅黑";
                            font-size: 18px;
                            font-weight: bold;
                            color:{self.theme["first"]};
                            background-color: {self.theme["background"]};
                            border: none;
                        }}
                        QPushButton:hover {{
                            background-color: {self.theme["first"]};
                            color:{self.theme["background"]}
                        }}
                    """)
        self.min_btn.clicked.connect(self.showMinimized)

        # 创建退出按钮
        self.exit_btn = QPushButton("X", self)
        self.exit_btn.setGeometry(
            main_btn_count * main_btn_width + min_btn_size,  # X位置
            0,  # Y位置
            exit_btn_size,  # 宽度
            exit_btn_size  # 高度
        )
        self.exit_btn.setStyleSheet(f"""
                        QPushButton {{
                            font-family: "微软雅黑";
                            font-size: 18px;
                            font-weight: bold;
                            color:{self.theme["first"]};
                            background-color: {self.theme["background"]};
                            border: none;
                            border-top-right-radius: 15px;
                        }}
                        QPushButton:hover {{
                            background-color: {self.theme["first"]};
                            color:{self.theme["background"]}
                        }}
                    """)
        self.exit_btn.clicked.connect(self.close_application)

        # 页面容器
        self.pages = QStackedWidget(self)
        self.pages.setGeometry(0, 50, self.width(), self.height() - 50)

        # 主页面

        # 新增模式选择容器
        self.default_page = QWidget(self.pages)
        self.model_container = QWidget(self.default_page)
        self.model_container.setGeometry(200, 100, 400, 200)
        self.model_container.hide()

        self.mode_container = QWidget(self.default_page)
        self.mode_container.setGeometry(200, 100, 400, 200)
        self.mode_container.hide()

        # 设置主布局
        self.controller.setup_main_layout()

        # 添加到页面
        self.pages.addWidget(self.default_page)

        self.pages.setCurrentWidget(self.default_page)

        # 日程页面
        self.schedule_page = SchedulePage()
        self.pages.addWidget(self.schedule_page)

        # ✅ 设置页面
        self.setting_page = SettingPage()
        self.pages.addWidget(self.setting_page)

        # ✅ 更多页面
        self.more_page = MorePage()
        self.pages.addWidget(self.more_page)

        self.show()

    def paintEvent(self, event):
        """绘制背景图片和圆角效果"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 创建圆角矩形路径
        path = QPainterPath()
        rect = self.rect()
        radius = 15.0  # 圆角半径
        path.addRoundedRect(QRectF(rect), radius, radius)  # 添加圆角矩形到路径

        # 设置裁剪区域（可选）
        painter.setClipPath(path)

        # 绘制背景图片（缩放适应窗口）
        scaled_pixmap = self.background_pixmap.scaled(
            self.size(),
            Qt.IgnoreAspectRatio,
            Qt.SmoothTransformation
        )
        painter.drawPixmap(0, 0, scaled_pixmap)

        # 绘制圆角边框（可选）
        pen = QPen(QColor(self.theme["background"]), 2)  # 边框颜色和宽度
        painter.setPen(pen)
        painter.drawPath(path)

    # 修改后的按钮鼠标事件处理
    def buttonMousePressEvent(self, button, event):
        """处理按钮上的鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.oldPos = event.globalPos()
            # 调用按钮的原始鼠标按下事件处理
            QPushButton.mousePressEvent(button, event)

    def buttonMouseMoveEvent(self, button, event):
        """处理按钮上的鼠标移动事件"""
        if self.dragging and event.buttons() & Qt.LeftButton:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
        else:
            # 调用按钮的原始鼠标移动事件处理
            QPushButton.mouseMoveEvent(button, event)

    def buttonMouseReleaseEvent(self, button, event):
        """处理按钮上的鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
            # 调用按钮的原始鼠标释放事件处理
            QPushButton.mouseReleaseEvent(button, event)

    def mousePressEvent(self, event):
        """处理面板本身的鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.oldPos = event.globalPos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """处理面板本身的鼠标移动事件"""
        if self.dragging and event.buttons() & Qt.LeftButton:
            delta = event.globalPos() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """处理面板本身的鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)

    def show_schedule_page(self):
        self.pages.setCurrentWidget(self.schedule_page)
        self.rounded_background.move_to_center_of(self.top_buttons["日程"], self)

    def show_main_page(self):
        self.pages.setCurrentWidget(self.default_page)
        self.rounded_background.move_to_center_of(self.top_buttons["启动"], self)

    def show_setting_page(self):
        self.pages.setCurrentWidget(self.setting_page)
        self.rounded_background.move_to_center_of(self.top_buttons["设置"], self)

    def show_more_page(self):
        self.pages.setCurrentWidget(self.more_page)
        self.rounded_background.move_to_center_of(self.top_buttons["更多"], self)

    def close_application(self):
        QApplication.instance().quit()