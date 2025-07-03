import os

from pet import DesktopPet, PetMode
from PyQt5.QtWidgets import (
    QPushButton, QDialog, QButtonGroup, QMessageBox,
    QVBoxLayout, QHBoxLayout, QLabel, QDialogButtonBox, QWidget, QSizePolicy, QGraphicsOpacityEffect,
    QGraphicsDropShadowEffect, QFrame, QStackedLayout
)
from PyQt5.QtGui import QPixmap, QTransform, QColor
from PyQt5.QtCore import QTimer, QSize, Qt, QPropertyAnimation, QRect, QEvent, QSequentialAnimationGroup, \
    QAbstractAnimation, QPoint, QEasingCurve, QParallelAnimationGroup

from setting_page import SettingPage
from utils import resource_path


class Controller:
    def __init__(self, ui):
        self.ui = ui
        self.selected_model = None
        self.model_names = ["小蓝鲸"]
        self.model_group = None  # 显式初始化按钮组
        self.model_animation_playing=False
        self.selected_mode = None
        self.mode_animation_playing=False
        self.mode_names = ["普通", "学习", "娱乐"]
        self.mode_group = None  # 显式初始化按钮组
        self.pet_instance = None

        # 初始化页面
        self.schedule_page = QWidget()
        self.setting_page = SettingPage()
        self.more_page = QWidget()
        self.theme=self.setting_page.load_theme()



    def setup_main_layout(self):
        """设置主页面的整体布局"""
        main_layout = QHBoxLayout(self.ui.default_page)  # 主水平布局

        # 左侧区域（白色背景）
        left_container = QWidget(self.ui.default_page)
        left_container.setStyleSheet(f"""background-color: {self.theme["background"]};
            border-radius: 20px;
            """)
        # 设置左侧区域的尺寸
        left_container.setFixedWidth(300)
        left_container.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        # 设置透明度
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.8)  # 设置透明度为 0.8（80%）
        left_container.setGraphicsEffect(opacity_effect)
        # 添加“模型”、“模式”、“运行”按钮到左侧布局
        self.setup_main_buttons(left_container)  # 主按钮设置方法
        # 添加左侧按钮区域
        main_layout.addWidget(left_container, alignment=Qt.AlignRight)

        # 添加“小蓝鲸”等按钮到右侧布局
        self.setup_model_buttons(self.ui.model_container)
        self.setup_mode_buttons(self.ui.mode_container)
        # 右侧区域使用 QStackedLayout 管理多个容器
        self.right_stack = QStackedLayout()
        # 初始显示空白页或 model_container
        self.blank_page = QWidget()  # 空白页
        # 添加空白页、模型页、模式页
        self.right_stack.addWidget(self.blank_page)  # 索引 0
        self.right_stack.addWidget(self.ui.model_container)  # 索引 1
        self.right_stack.addWidget(self.ui.mode_container)  # 索引 2
        # 初始显示空白页
        self.right_stack.setCurrentIndex(0)
        # 创建一个容器 widget 包裹 stacked layout
        right_widget = QWidget()
        right_widget.setLayout(self.right_stack)
        main_layout.addWidget(right_widget)

        self.ui.default_page.setLayout(main_layout)

    def setup_main_buttons(self, page):
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignBottom |  Qt.AlignCenter)

        # 模型按钮
        self.ui.model_btn = QPushButton("模型", page)
        self.ui.model_btn.clicked.connect(self.show_model_selection)

        # 模式按钮
        self.ui.mode_btn = QPushButton("模式", page)
        self.ui.mode_btn.clicked.connect(self.show_mode_selection)

        # 运行按钮
        self.run_btn = QPushButton("运行", page)
        self.run_btn.clicked.connect(self.check_before_run)

        # 统一样式
        button_style = f"""
            QPushButton {{
                font-family: "微软雅黑";
                background-color: {self.theme["fourth"]};
                color: white;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                border:3px  solid {self.theme["second"]};
            }}
            QPushButton:hover {{ background-color: {self.theme["third"]}; border-color: {self.theme["second"]}; }}
            QPushButton:pressed {{ background-color: {  self.theme["third"]}; border-color: {self.theme["second"]}; }}
        """
        self.ui.model_btn.setStyleSheet(button_style)
        self.ui.mode_btn.setStyleSheet(button_style)
        self.run_btn.setStyleSheet(button_style)
        self.ui.model_btn.setFixedWidth(280)  # 设置按钮宽度为 280 像素
        self.ui.mode_btn.setFixedWidth(280)
        self.run_btn.setFixedWidth(280)
        self.ui.model_btn.animation_playing=False
        self.ui.mode_btn.animation_playing=False
        self.run_btn.animation_playing=False

        # 添加动画逻辑
        for btn in [self.ui.model_btn, self.ui.mode_btn, self.run_btn]:
            self._add_button_animation(btn)

        # 创建 QLabel 实例来显示图片
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        image_label = QLabel(page)
        # 加载并缩放图片
        original_pixmap = QPixmap(resource_path("model/png/building.png"))  # 替换为实际的图片路径
        scaled_pixmap = original_pixmap.scaled(600,600, Qt.KeepAspectRatio)  # 调整图片大小
        # 设置图片透明度
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.25)  # 设置透明度为 0.8（可根据需要调整）
        image_label.setGraphicsEffect(opacity_effect)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignCenter)  # 图片居中显示

        # 将 QLabel 添加到布局中
        layout.addWidget(image_label)
        layout.addSpacing(100)  # 添加间距

        # 添加按钮与间距
        layout.addWidget(self.ui.model_btn)
        layout.addSpacing(10)  # 模型和模式之间加 20px 间距
        layout.addWidget(self.ui.mode_btn)
        layout.addSpacing(10)  # 模式和运行之间加 20px 间距
        layout.addWidget(self.run_btn)

        page.setLayout(layout)

    def _add_button_animation(self, button):
        """为按钮添加点击时震动并放大的动画"""
        original_size = button.size()
        pressed_size = original_size * 1.15  # 放大 15%

        def animate_press():
            if getattr(button, 'animation_playing', False):
                return
            button.animation_playing = True

            original_size = button.size()
            pressed_size = original_size * 1.1

            # 保存原始尺寸和位置
            button.setProperty("original_size", original_size)
            button.setProperty("original_pos", button.pos())

            # 创建放大动画
            scale_animation = QPropertyAnimation(button, b"size")
            scale_animation.setDuration(100)
            scale_animation.setStartValue(original_size)
            scale_animation.setEndValue(pressed_size)
            scale_animation.setEasingCurve(QEasingCurve.OutQuad)

            # 创建震动动画（左右晃动）
            pos_animation = QPropertyAnimation(button, b"pos")
            pos_animation.setDuration(100)
            pos_animation.setLoopCount(2)
            pos_animation.setKeyValueAt(0.0, button.pos())
            pos_animation.setKeyValueAt(0.3, button.pos() + QPoint(5, 0))
            pos_animation.setKeyValueAt(0.6, button.pos() + QPoint(-5, 0))
            pos_animation.setKeyValueAt(1.0, button.pos())

            animation_group = QParallelAnimationGroup()
            animation_group.addAnimation(scale_animation)
            animation_group.addAnimation(pos_animation)

            def on_finished():
                button.animation_playing = False
                animate_release()

            animation_group.finished.connect(on_finished)
            animation_group.start()

            button._current_animation = animation_group

        def animate_release():
            if getattr(button, 'animation_playing', False):
                return
            button.animation_playing = True

            original_size = button.property("original_size")
            original_pos = button.property("original_pos")

            if not original_size or not original_pos:
                return

            # 缩小动画：从当前大小回到原始大小
            scale_animation = QPropertyAnimation(button, b"size")
            scale_animation.setDuration(100)
            scale_animation.setStartValue(button.size())
            scale_animation.setEndValue(original_size)

            # 回到原位动画
            pos_animation = QPropertyAnimation(button, b"pos")
            pos_animation.setDuration(100)
            pos_animation.setStartValue(button.pos())
            pos_animation.setEndValue(original_pos)

            animation_group = QParallelAnimationGroup()
            animation_group.addAnimation(scale_animation)
            animation_group.addAnimation(pos_animation)

            def on_finished():
                button.animation_playing = False

            animation_group.finished.connect(on_finished)
            animation_group.start()

            button._current_animation = animation_group

        # 鼠标按下时触发放大动画
        button.pressed.connect(animate_press)

    def setup_model_buttons(self, container):
        """初始化模型选择按钮"""
        if self.model_group:
            self.model_group.deleteLater()
            self.model_group = None

        self.model_group = QButtonGroup(container)

        for child in container.findChildren(QPushButton):
            child.deleteLater()

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignHCenter)

        # 创建按钮
        for i in range(0, 1):
            btn = QPushButton(f"{self.model_names[i]}", container)

            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-family: "微软雅黑";  /* 字体名称 */
                    font-size: 16px;        /* 字号 */
                    color:black;
                    background-color: white;
                    padding: 8px;
                    font-size: 16px;
                    border-radius: 10px;
                    min-width: 320px;
                }}
                QPushButton:checked {{
                    background-color: {self.theme["second"]};
                    border-color: #4682B4;
                }}
            """)
            # 连接鼠标进入/离开事件
            btn.enterEvent = lambda e, b=btn: self.start_button_animation(b, True)
            btn.leaveEvent = lambda e, b=btn: self.start_button_animation(b, False)
            self.model_group.addButton(btn, i)
            layout.addWidget(btn)

        # 敬请期待提示按钮
        more_btn = QPushButton("......（敬请期待）", container)
        more_btn.setStyleSheet("""
                           QPushButton {
                               font-family: "微软雅黑";
                               font-size: 16px;
                               background-color: #EEEEEE;
                               border-radius: 10px;
                               padding: 8px;
                           }
                       """)
        layout.addWidget(more_btn)
        more_btn.enterEvent = lambda e, b=more_btn: self.start_button_animation(b, True)
        more_btn.leaveEvent = lambda e, b=more_btn: self.start_button_animation(b, False)

        # 确认按钮
        confirm_btn = QPushButton("确认选择", container)
        confirm_btn.clicked.connect(lambda: self.save_model_selection())
        confirm_btn.setStyleSheet(f"""
                   QPushButton {{
                       font-family: "微软雅黑";
                       color: white;
                       font-size: 16px;
                       font-weight: bold;
                       background-color: {self.theme["background"]};
                       border-radius: 10px;
                       padding: 8px;
                   }}
               """)
        layout.addWidget(confirm_btn)
        confirm_btn.enterEvent = lambda e, b=confirm_btn: self.start_button_animation(b, True)
        confirm_btn.leaveEvent = lambda e, b=confirm_btn: self.start_button_animation(b, False)

        container.setLayout(layout)


    def start_button_animation(self, button, enlarge):
        if getattr(self, "model_animation_playing", False) or getattr(self,"mode_animation_playing",False):
            return
        """使用几何动画实现按钮放大/缩小"""
        original_geo = button.property("original_geometry")
        if not original_geo:
            original_geo = button.geometry()
            button.setProperty("original_geometry", original_geo)

        if enlarge:
            # 添加阴影效果
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 0)
            button.setGraphicsEffect(shadow)
            #放大
            new_width = int(original_geo.width() * 1.1)
            new_height = int(original_geo.height() * 1.1)
            x = original_geo.x() - (new_width - original_geo.width()) // 2
            y = original_geo.y() - (new_height - original_geo.height()) // 2
            target_geo = QRect(x, y, new_width, new_height)
        else:
            # 移除阴影效果
            button.setGraphicsEffect(None)
            target_geo = original_geo

        # 如果之前有动画正在运行，先停止
        if hasattr(button, "_button_animation"):
            button._button_animation.stop()

        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(200)
        animation.setStartValue(button.geometry())
        animation.setEndValue(target_geo)
        button._button_animation = animation  # 防止重复播放
        animation.start()



    #老代码，已弃用
    #
    # def show_model_selection(self):
    #     dialog = QDialog(self.ui)
    #     dialog.setWindowTitle("选择模型")
    #     dialog.setFixedSize(600, 400)
    #
    #     layout = QVBoxLayout()
    #     btn_layout = QHBoxLayout()
    #
    #     image_paths = []
    #     self.model_group = QButtonGroup(dialog)
    #
    #     for idx, path in enumerate(image_paths):
    #         btn = QPushButton(dialog)
    #         btn.setFixedSize(150, 150)
    #         pixmap = QPixmap(path).scaled(140, 140, Qt.KeepAspectRatio)
    #         btn.setIcon(pixmap)
    #         btn.setIconSize(QSize(140, 140))
    #         self.model_group.addButton(btn, idx)
    #         btn_layout.addWidget(btn)
    #
    #     button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    #     button_box.accepted.connect(lambda: self.save_model_selection(dialog))
    #     button_box.rejected.connect(dialog.reject)
    #
    #     layout.addLayout(btn_layout)
    #     layout.addWidget(button_box)
    #     dialog.setLayout(layout)
    #     dialog.exec_()

    def setup_mode_buttons(self, container):
        """初始化模式选择按钮"""
        self.mode_group = QButtonGroup(container)

        for child in container.findChildren(QPushButton):
            child.deleteLater()

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignCenter)

        # 创建三个模式按钮
        for i in range(0, 3):
            btn = QPushButton(f"{self.mode_names[i]}模式", container)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-family: "微软雅黑";  /* 字体名称 */
                    font-size: 16px;        /* 字号 */
                    background-color: white;
                    padding: 8px;
                    border-radius: 10px;
                    font-size: 16px;
                    min-width: 320px;
                }}
                QPushButton:checked {{
                    background-color: {self.theme["second"]};
                    border-color: #4682B4;
                }}
            """)
            btn.enterEvent = lambda e, b=btn: self.start_button_animation(b, True)
            btn.leaveEvent = lambda e, b=btn: self.start_button_animation(b, False)
            self.mode_group.addButton(btn, i)
            layout.addWidget(btn)

        # 确认按钮
        confirm_btn = QPushButton("确认选择", container)
        confirm_btn.clicked.connect(lambda: self.save_mode_selection())
        confirm_btn.setStyleSheet(f"""
                   QPushButton {{
                       font-family: "微软雅黑";
                       font-size: 16px;
                       font-weight: bold;
                       color: white;
                       border-radius: 10px;
                       background-color: {self.theme["background"]};
                       padding: 8px;
                   }}
               """)
        confirm_btn.enterEvent = lambda e, b=confirm_btn: self.start_button_animation(b, True)
        confirm_btn.leaveEvent = lambda e, b=confirm_btn: self.start_button_animation(b, False)
        layout.addWidget(confirm_btn)

        container.setLayout(layout)



    def save_model_selection(self):
        """保存模型选择，并触发动画退出"""
        if selected_btn := self.model_group.checkedButton():
            self.selected_model = self.model_group.id(selected_btn)
            self.ui.model_btn.setText(f"模型：{self.model_names[self.selected_model]}")

            # 执行退出动画
            self.exit_model_selection()
        else:
            QMessageBox.warning(self.ui, "警告", "请先选择一个模型！")

    def exit_model_selection(self):
        """隐藏模型选择区域，按钮逐个淡出+上移"""
        # 防止重复触发动画
        if getattr(self, "model_animation_playing", False):
            return
        self.model_animation_playing = True

        self.ui.model_btn.setEnabled(False)
        widget = self.ui.model_container
        buttons = widget.findChildren(QPushButton)

        for idx, btn in enumerate(buttons):
            original_geo = btn.property("original_geometry")
            if not original_geo:
                original_geo = btn.geometry()
                btn.setProperty("original_geometry", original_geo)
            # 获取目标位置
            original_pos=btn.pos()
            target_pos = QPoint(btn.x(), btn.y() - 150)

            # 创建透明度特效
            opacity_effect = QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(opacity_effect)

            # 创建透明度动画
            opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
            opacity_animation.setDuration(400)
            opacity_animation.setStartValue(1.0)
            opacity_animation.setEndValue(0.0)

            # 创建位置动画
            pos_animation = QPropertyAnimation(btn, b"pos")
            pos_animation.setDuration(300)
            pos_animation.setStartValue(btn.pos())
            pos_animation.setEndValue(target_pos)
            pos_animation.setEasingCurve(QEasingCurve.InOutQuad)

            # 使用并行动画组
            animation_group = QParallelAnimationGroup()
            animation_group.addAnimation(opacity_animation)
            animation_group.addAnimation(pos_animation)

            def on_animation_finished(
                    btn=btn,
                    original_pos=original_pos,
                    anim=animation_group
            ):
                btn.move(original_pos.x(),  original_pos.y())
                btn.setGeometry(btn.property("original_geometry"))
                if idx==len(buttons)-1:
                    self.model_animation_playing = False
                    self.right_stack.setCurrentIndex(0)
                    QTimer.singleShot(100, lambda : self.ui.model_btn.setEnabled(True))
                anim.deleteLater()

            animation_group.finished.connect(on_animation_finished)

            # 保存引用防止被回收
            btn.animation_group = animation_group

            # 增加延迟启动，按钮之间间隔 60ms
            delay = idx * 60
            QTimer.singleShot(delay, btn.animation_group.start)

    def show_model_selection(self):
        """显示模型选择区域，按钮逐个淡入+上浮"""
        # 防止重复触发动画
        if getattr(self, "model_animation_playing", False):
            return
        self.model_animation_playing = True

        # 隐藏其他面板
        self.right_stack.setCurrentWidget(self.ui.model_container)

        # 显示模型选择区域
        widget = self.ui.model_container

        buttons = widget.findChildren(QPushButton)

        for idx, btn in enumerate(buttons):
            # 获取目标位置
            target_pos = btn.pos()

            # 设置初始位置（屏幕下方）
            btn.move(target_pos.x(), target_pos.y() + 150)

            # 创建透明度特效
            opacity_effect = QGraphicsOpacityEffect(btn)
            opacity_effect.setOpacity(0.0)  # 设置初始透明度为 0
            btn.setGraphicsEffect(opacity_effect)

            # 创建透明度动画
            opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
            opacity_animation.setDuration(400)
            opacity_animation.setStartValue(-0.0)
            opacity_animation.setEndValue(1.0)

            # 创建位置动画
            pos_animation = QPropertyAnimation(btn, b"pos")
            pos_animation.setDuration(300)
            pos_animation.setStartValue(btn.pos())
            pos_animation.setEndValue(target_pos)
            pos_animation.setEasingCurve(QEasingCurve.InOutQuad)

            # 使用并行动画组
            animation_group = QParallelAnimationGroup()
            animation_group.addAnimation(opacity_animation)
            animation_group.addAnimation(pos_animation)

            if idx == len(buttons) - 1:
                def on_animation_finished():
                    self.model_animation_playing = False
                    animation_group.deleteLater()

                animation_group.finished.connect(on_animation_finished)

            # 保存引用防止被回收
            btn.animation_group = animation_group

            # 增加延迟启动，按钮之间间隔 60ms
            delay = idx * 60
            QTimer.singleShot(delay, btn.animation_group.start)

    def save_mode_selection(self):
        """保存模式选择，并触发动画退出"""
        if selected_btn := self.mode_group.checkedButton():
            self.selected_mode = self.mode_group.id(selected_btn)
            self.ui.mode_btn.setText(f"模式：{self.mode_names[self.selected_mode]}")

            # 执行退出动画
            self.exit_mode_selection()

            # 延迟切换页面
            QTimer.singleShot(500, lambda: self.right_stack.setCurrentIndex(0))
        else:
            QMessageBox.warning(self.ui, "警告", "请先选择一个模式！")

    def exit_mode_selection(self):
        """隐藏模型选择区域，按钮逐个淡出+上移"""
        # 防止重复触发动画
        if getattr(self, "mode_animation_playing", False):
            return
        self.mode_animation_playing = True

        self.ui.mode_btn.setEnabled(False)
        widget = self.ui.mode_container
        buttons = widget.findChildren(QPushButton)

        for idx, btn in enumerate(buttons):
            original_geo = btn.property("original_geometry")
            if not original_geo:
                original_geo = btn.geometry()
                btn.setProperty("original_geometry", original_geo)
            # 获取目标位置
            original_pos=btn.pos()
            target_pos = QPoint(btn.x(), btn.y() - 150)

            # 创建透明度特效
            opacity_effect = QGraphicsOpacityEffect(btn)
            btn.setGraphicsEffect(opacity_effect)

            # 创建透明度动画
            opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
            opacity_animation.setDuration(400)
            opacity_animation.setStartValue(1.0)
            opacity_animation.setEndValue(0.0)

            # 创建位置动画
            pos_animation = QPropertyAnimation(btn, b"pos")
            pos_animation.setDuration(300)
            pos_animation.setStartValue(btn.pos())
            pos_animation.setEndValue(target_pos)
            pos_animation.setEasingCurve(QEasingCurve.InOutQuad)

            # 使用并行动画组
            animation_group = QParallelAnimationGroup()
            animation_group.addAnimation(opacity_animation)
            animation_group.addAnimation(pos_animation)

            def on_animation_finished(
                    btn=btn,
                    original_pos=original_pos,
                    anim=animation_group
            ):
                btn.move(original_pos.x(),  original_pos.y())
                btn.setGeometry(btn.property("original_geometry"))
                if idx==len(buttons)-1:
                    self.mode_animation_playing = False
                    self.right_stack.setCurrentIndex(0)
                    QTimer.singleShot(100, lambda : self.ui.mode_btn.setEnabled(True))
                anim.deleteLater()

            animation_group.finished.connect(on_animation_finished)

            # 保存引用防止被回收
            btn.animation_group = animation_group

            # 增加延迟启动，按钮之间间隔 60ms
            delay = idx * 60
            QTimer.singleShot(delay, btn.animation_group.start)

    def show_mode_selection(self):
        """显示/隐藏模式选择区域"""
        # 防止重复触发动画
        if getattr(self, "mode_animation_playing", False):
            return
        self.mode_animation_playing = True

        self.right_stack.setCurrentWidget(self.ui.mode_container)

        # 显示模型选择区域
        widget = self.ui.mode_container

        buttons = widget.findChildren(QPushButton)

        for idx, btn in enumerate(buttons):
            # 获取目标位置
            target_pos = btn.pos()

            # 设置初始位置（屏幕下方）
            btn.move(target_pos.x(), target_pos.y() + 150)

            # 创建透明度特效
            opacity_effect = QGraphicsOpacityEffect(btn)
            opacity_effect.setOpacity(0.0)  # 设置初始透明度为 0
            btn.setGraphicsEffect(opacity_effect)

            # 创建透明度动画
            opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
            opacity_animation.setDuration(400)
            opacity_animation.setStartValue(0.0)
            opacity_animation.setEndValue(1.0)

            # 创建位置动画
            pos_animation = QPropertyAnimation(btn, b"pos")
            pos_animation.setDuration(300)
            pos_animation.setStartValue(btn.pos())
            pos_animation.setEndValue(target_pos)
            pos_animation.setEasingCurve(QEasingCurve.InOutQuad)

            # 使用并行动画组
            animation_group = QParallelAnimationGroup()
            animation_group.addAnimation(opacity_animation)
            animation_group.addAnimation(pos_animation)

            if idx == len(buttons) - 1:
                def on_animation_finished():
                    self.mode_animation_playing = False
                    animation_group.deleteLater()

                animation_group.finished.connect(on_animation_finished)

            # 保存引用防止被回收
            btn.animation_group = animation_group

            # 增加延迟启动，按钮之间间隔 60ms
            delay = idx * 60
            QTimer.singleShot(delay, btn.animation_group.start)

    def check_before_run(self):
        if self.selected_model == None or self.selected_mode == None:
            QMessageBox.warning(self.ui, "警告", "请先选择模型和模式！")
        else:
            self.show_success_message()
            self.run_desktop_pet()

    def show_success_message(self):
        success_label = QLabel(" 启动成功！", self.ui)
        success_label.setStyleSheet(f"""
            QLabel {{
                font-family: "微软雅黑";
                font-size: 24px;
                font-weight: bold;
                background-color: {self.theme["background"]};
                color: {self.theme["first"]};
                padding: 10px;
                border-radius: 10px;
                border: 2px solid {self.theme["first"]};
            }}
        """)
        success_label.setGeometry(
            self.ui.width() // 2 - 80,
            self.ui.height() // 2 - 40,
            160,
            80
        )
        success_label.show()
        QTimer.singleShot(3000, success_label.hide)

    def run_desktop_pet(self):
        """创建并显示桌宠窗口"""
        # 销毁旧实例
        if self.pet_instance:
            self.pet_instance.close()
            self.pet_instance.deleteLater()
            self.pet_instance = None

        # 创建新实例
        if self.pet_instance is None:
            mode = PetMode.NORMAL
            if self.selected_mode == 1:
                mode = PetMode.STUDY
            elif self.selected_mode == 2:
                mode = PetMode.ENTERTAIN
            self.pet_instance = DesktopPet(mode, self.setting_page)
        self.pet_instance.show()

    # 页面切换方法
    def show_schedule_page(self):
        self.ui.pages.setCurrentWidget(self.schedule_page)

    def show_main_page(self):
        self.ui.pages.setCurrentWidget(self.ui.default_page)

    def show_setting_page(self):
        self.ui.pages.setCurrentWidget(self.setting_page)

    def show_more_page(self):
        self.ui.pages.setCurrentWidget(self.more_page)

    def close_application(self):
        self.ui.close()