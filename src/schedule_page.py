from PyQt5.QtWidgets import (QWidget, QCalendarWidget, QPushButton, QDialog,
                             QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
                             QLabel, QTimeEdit, QMessageBox, QSizePolicy, QScrollArea,
                             QFrame, QGridLayout, QToolTip)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QColor, QTextCharFormat, QBrush
import json
import os


class SchedulePage(QWidget):
    def __init__(self):
        super().__init__()
        self.schedules = {}
        self.load_schedules()
        self.initUI()
        self.calendar.installEventFilter(self)

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout(self)

        # 日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.update_calendar_style()
        main_layout.addWidget(self.calendar)

        # 加号按钮
        self.add_btn = QPushButton("+", self)
        self.add_btn.setFixedSize(40, 40)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border-radius: 20px;
                color: white;
                font-size: 24px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_btn.clicked.connect(self.show_add_dialog)
        self.calendar.activated.connect(self.handle_date_click)  # 双击触发

        # 初始化加载已有日程
        self.highlight_dates()

    def resizeEvent(self, event):
        # 保持按钮在右下角
        btn_size = self.add_btn.size()
        self.add_btn.move(self.width() - btn_size.width() - 10,
                          self.height() - btn_size.height() - 10)
        super().resizeEvent(event)

    def update_calendar_style(self):
        # 日历样式
        self.calendar.setStyleSheet("""
            QCalendarWidget QWidget {
                alternate-background-color: #f0f0f0;
                font-family: 16px;
            }
            QCalendarWidget QToolButton {
                font-size: 14px;
            }
            QCalendarWidget QAbstractItemView:enabled {
                selection-background-color: #007BFF;
                selection-color: white;
                alternate-background-color: #f5f5f5;
            }
        """)

    def eventFilter(self, source, event):
        if event.type() == event.ToolTip and source is self.calendar:
            date = self.calendar.selectedDate()
            date_str = date.toString("yyyy-MM-dd")
            if date_str in self.schedules:
                titles = "\n".join([s["title"] for s in self.schedules[date_str]])
                QToolTip.showText(event.globalPos(), f"日程:\n{titles}")
            else:
                QToolTip.hideText()
            return True
        return super().eventFilter(source, event)

    def show_add_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("添加日程")
        dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowMinMaxButtonsHint)
        dialog.setMinimumSize(380, 560)
        dialog.resize(380, 560)

        main_layout = QVBoxLayout(dialog)

        # ======= 输入控件 =======
        self.date_edit = QCalendarWidget()
        self.date_edit.setMinimumDate(QDate.currentDate())
        self.time_edit = QTimeEdit()
        self.title_edit = QLineEdit()
        self.detail_edit = QTextEdit()

        # ======= 自适应布局 =======
        main_layout.addWidget(QLabel("日期:"))
        main_layout.addWidget(self.date_edit)
        main_layout.addWidget(QLabel("时间:"))
        main_layout.addWidget(self.time_edit)
        main_layout.addWidget(QLabel("标题:"))
        main_layout.addWidget(self.title_edit)
        main_layout.addWidget(QLabel("详情:"))
        main_layout.addWidget(self.detail_edit, stretch=1)  # 详情框自动扩展

        # 设置尺寸策略
        self.date_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.detail_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ======= 底部按钮布局 =======
        btn_layout = QHBoxLayout()
        confirm_btn = QPushButton("确认")
        confirm_btn.clicked.connect(lambda: self.save_schedule(dialog))
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        help_btn = QPushButton("帮助")
        btn_layout.addStretch(1)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(help_btn)
        btn_layout.addWidget(cancel_btn)

        main_layout.addLayout(btn_layout)

        # ======= 帮助系统 =======
        def show_help():
            QMessageBox.information(
                dialog, "帮助",
                "1. 选择未来日期和时间\n"
                "2. 标题为必填项（最多20字）\n"
                "3. 详情可输入多行文本\n"
                "4. 已有日程的日期会高亮显示\n"
                "5. 双击高亮的日期可以查看日程"
            )

        help_btn.clicked.connect(show_help)
        dialog.exec_()

    def save_schedule(self, dialog):
        # 获取输入内容
        date = self.date_edit.selectedDate().toString("yyyy-MM-dd")
        time = self.time_edit.time().toString("hh:mm")
        title = self.title_edit.text()
        detail = self.detail_edit.toPlainText()

        if not title:
            QMessageBox.warning(self, "警告", "标题不能为空！")
            return

        # 保存到数据结构
        schedule = {
            "time": time,
            "title": title,
            "detail": detail
        }

        if date not in self.schedules:
            self.schedules[date] = []
        self.schedules[date].append(schedule)

        # 更新日历显示
        self.highlight_dates()
        self.save_to_file()
        dialog.accept()

    def highlight_dates(self):
        # 清除所有高亮
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())

        # 高亮有日程的日期
        fmt = QTextCharFormat()
        fmt.setBackground(QBrush(QColor(255, 255, 0, 100)))

        for date_str in self.schedules:
            date = QDate.fromString(date_str, "yyyy-MM-dd")
            if date.isValid():
                self.calendar.setDateTextFormat(date, fmt)

    def load_schedules(self):
        # 从文件加载数据
        base_path=os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(base_path, "schedules.json")):
            try:
                with open(os.path.join(base_path, "schedules.json"), "r", encoding="utf-8") as f:
                    self.schedules = json.load(f)
            except:
                self.schedules = {}

    def save_to_file(self):
        # 保存数据到文件
        base_path = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_path, "schedules.json"), "w", encoding="utf-8") as f:
            json.dump(self.schedules, f, ensure_ascii=False, indent=2)

    def handle_date_click(self, date):
        date_str = date.toString("yyyy-MM-dd")
        if date_str in self.schedules:
            self.show_schedule_details(date_str)

    def show_schedule_details(self, date):
        # 显示当天所有日程
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{date} 的日程")
        dialog.setMinimumSize(400, 400)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)

        # 添加删除该日所有日程的按钮
        delete_day_btn = QPushButton("删除本日所有日程")
        delete_day_btn.setStyleSheet("""
            QPushButton {
                font-family: "微软雅黑";  /* 字体名称 */
                background-color: #ff6b6b;
                color: white;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
        """)
        delete_day_btn.clicked.connect(lambda: self.delete_day_schedules(date, dialog))
        layout.addWidget(delete_day_btn)

        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #ddd;")
        layout.addWidget(separator)

        # 添加每个日程项
        for idx, schedule in enumerate(self.schedules[date]):
            # 每个日程项使用框架包裹
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            frame_layout = QGridLayout(frame)

            # 时间
            time_label = QLabel(f"⏰ {schedule['time']}")
            time_label.setStyleSheet("""
                        QLabel {
                            font-family: "微软雅黑";
                            font-size: 16px;
                            color: #212529;
                        }
                    """)
            frame_layout.addWidget(time_label, 0, 0)

            # 标题
            title_label = QLabel(f"📌 {schedule['title']}")
            title_label.setStyleSheet("""
                        QLabel {
                            font-family: "微软雅黑";
                            font-size: 16px;
                            color: #212529;
                        }
                    """)
            frame_layout.addWidget(title_label, 1, 0)

            # 详情
            detail_label = QLabel(f"📝 {schedule['detail']}")
            detail_label.setStyleSheet("""
                        QLabel {
                            font-family: "微软雅黑";
                            font-size: 16px;
                            color: #212529;
                        }
                    """)
            detail_label.setWordWrap(True)
            frame_layout.addWidget(detail_label, 2, 0)

            # 删除按钮
            delete_btn = QPushButton("删除")
            delete_btn.setStyleSheet("""
                QPushButton {
                    font-family: "微软雅黑";
                    font-size: 16px;
                    background-color: #ff6b6b;
                    color: white;
                    padding: 8px 10px;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #ff5252;
                }
            """)
            delete_btn.setFixedWidth(80)
            delete_btn.clicked.connect(lambda _, d=date, i=idx: self.delete_single_schedule(d, i, dialog))
            frame_layout.addWidget(delete_btn, 0, 1, 3, 1, Qt.AlignTop | Qt.AlignRight)

            layout.addWidget(frame)

        # 如果没有日程
        if not self.schedules[date]:
            layout.addWidget(QLabel("该日没有日程安排"), alignment=Qt.AlignCenter)

        scroll_area.setWidget(content_widget)

        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(scroll_area)
        dialog.exec_()

    def delete_single_schedule(self, date, index, dialog):
        """删除单个日程"""
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {date} 的日程 '{self.schedules[date][index]['title']}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 删除日程
            del self.schedules[date][index]

            # 如果该日没有日程了，删除整个日期
            if not self.schedules[date]:
                del self.schedules[date]
                # 更新日历高亮
                self.highlight_dates()

            # 保存更改
            self.save_to_file()

            # 关闭并重新打开对话框以刷新显示
            dialog.accept()
            if date in self.schedules:  # 如果还有其他日程，重新打开
                self.show_schedule_details(date)
            else:
                QMessageBox.information(self, "删除成功", "日程已成功删除！")

    def delete_day_schedules(self, date, dialog):
        """删除整个日期的所有日程"""
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {date} 的所有日程吗？共 {len(self.schedules[date])} 个日程。",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # 删除该日所有日程
            del self.schedules[date]

            # 更新日历高亮
            self.highlight_dates()

            # 保存更改
            self.save_to_file()

            # 关闭对话框并提示
            dialog.accept()
            QMessageBox.information(self, "删除成功", f"{date} 的所有日程已成功删除！")

    def get_today_schedules(self):
        """获取今日所有日程（供外部调用）"""
        today = QDate.currentDate().toString("yyyy-MM-dd")
        return self.schedules.get(today, [])