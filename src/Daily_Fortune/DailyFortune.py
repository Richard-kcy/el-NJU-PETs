import uuid
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialog, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from .EditFortunes import EditFortuneDialog
import random
import json
import os
from datetime import datetime, timedelta

class DailyFortuneWindow(QDialog):
    def load_fortunes(self):
        file_path = os.path.join(os.path.dirname(__file__), "fortunes.json")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print("加载运势配置失败:", e)
            return {
                "yi": [],
                "ji": []
            }

    # 打卡记录文件路径
    FILE = os.path.join(os.path.dirname(__file__), "checkin_record.json")

    def get_checkin_info(self):
        if not os.path.exists(self.FILE):
            return {"last_date": None, "streak": 0}

        with open(self.FILE, "r") as f:
            return json.load(f)

    def save_checkin_info(self,last_date, streak):
        try:
            with open(self.FILE, "w") as f:
                json.dump({"last_date": str(last_date), "streak": streak}, f)
        except IOError as e:
            print("保存打卡信息失败:", e)

    def check_in(self):
        now = datetime.now().date()
        record = self.get_checkin_info()

        last_date_str = record["last_date"]
        streak = record["streak"]

        if last_date_str is None:
            # 首次打卡
            new_streak = 1
        else:
            last_date = datetime.fromisoformat(last_date_str).date()

            if (now - last_date).days == 1:
                # 昨天打卡了，连续天数+1
                new_streak = streak + 1
            elif (now - last_date).days == 0:
                # 今天已经打过卡了，不重复计数
                new_streak = streak
            else:
                # 中断了，重置为 1
                new_streak = 1

        # 更新记录
        self.save_checkin_info(str(now), new_streak)
        return new_streak

    def get_daily_random_pair(self,seed_str,min_val, max_val):
        # 设置种子
        random.seed(seed_str)

        # 生成两个不同的随机数
        num1 = random.randint(min_val, max_val)
        num2 = random.randint(min_val, max_val)

        # 确保两个数不同
        while num2 == num1:
            num2 = random.randint(min_val, max_val)

        return num1, num2

    def __init__(self,parent=None):
        super().__init__(parent,flags=Qt.Window |  Qt.WindowStaysOnTopHint)
        self.setWindowTitle("今日运势")
        # 设置窗口图标
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "DailyFortuneIcon.png")  # 图标文件路径
        self.setWindowIcon(QIcon(icon_path))  # 设置图标
        self.resize(400, 300)
        self.initUI()

    def initUI(self):
        # 主布局
        main_layout = QVBoxLayout()

        # 标题部分
        title = [
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#FF0000;'>§ 大吉大利 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#FF4500;'>§ 上上签 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#FF8C00;'>§ 天降鸿运 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#FFA500;'>§ 吉星高照 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#FFD700;'>§ 中吉 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#FFFF00;'>§ 小吉 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#ADFF2F;'>§ 平稳 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#32CD32;'>§ 顺遂 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#00BFFF;'>§ 平平 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#1E90FF;'>§ 中平 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#4682B4;'>§ 无咎 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#9370DB;'>§ 小凶 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#8A2BE2;'>§ 宜谨慎 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#A9A9A9;'>§ 有波折 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#800080;'>§ 大凶 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#4B0082;'>§ 下下签 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#2F4F4F;'>§ 诸事不宜 §</span>""",
            f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:#000000;'>§ 黑云压顶 §</span>"""
        ]

        # 获取当前日期
        today = datetime.now()
        # 获取设备唯一标识
        device_code = str(uuid.getnode())
        # 使用年月日作为种子（固定格式）
        seed_str = f"{today.year}{today.month}{today.day}_{device_code}"
        # 设置种子
        random.seed(seed_str)
        # 生成两个不同的随机数
        num = random.randint(0, len(title)-1)
        title_label = QLabel(self)
        title_label.setText(title[num])
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 宜 忌 部分
        self.yi_ji_layout = QHBoxLayout()
        self.setup_yi_ji_layout(self.yi_ji_layout)
        main_layout.addLayout(self.yi_ji_layout)

        # 获取当前连续打卡天数
        current_streak = self.check_in()
        # 底部提示
        bottom_label = QLabel(f"你已经连续打卡了 {current_streak} 天", self)
        bottom_label.setAlignment(Qt.AlignCenter)
        bottom_label.setStyleSheet("font-size: 16px; color: #333;")
        main_layout.addWidget(bottom_label)
        # 添加按钮允许用户编辑提示词
        self.add_button = QPushButton("+", self)
        self.add_button.setFixedSize(40, 40)
        self.add_button.setStyleSheet("""
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
        self.add_button.clicked.connect(self.open_edit_dialog)

        # 将按钮放在主布局的右下角
        main_layout.addWidget(self.add_button, alignment=Qt.AlignRight | Qt.AlignBottom)
        self.setLayout(main_layout)

    def open_edit_dialog(self):
        fortunes = self.load_fortunes()
        dialog = EditFortuneDialog(self, data=fortunes)
        dialog.exec_()
        # 保存数据到 JSON 文件
        file_path = os.path.join(os.path.dirname(__file__), "fortunes.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(dialog.data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "成功", "配置已保存！")
            #刷新 宜 忌 部分
            self.refresh_yi_ji()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def setup_yi_ji_layout(self, layout):
        fortunes = self.load_fortunes()
        yi_list = fortunes["yi"]
        ji_list = fortunes["ji"]

        today = datetime.now()
        device_code = str(uuid.getnode())
        seed_str = f"{today.year}{today.month}{today.day}_{device_code}"
        random.seed(seed_str)

        # 宜 部分
        yi_layout = QVBoxLayout()
        yi_layout.setAlignment(Qt.AlignCenter)

        var1, var2 = self.get_daily_random_pair(seed_str, 0, len(yi_list) - 1)
        for var in [var1, var2]:
            label = QLabel()
            label.setText(f"""
                <span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:18px; color:#C10103;'>宜：</span><!--
             --><span style='font-family: 微软雅黑, SimHei, sans-serif;font-size:18px; color:#ff0000;'>{yi_list[var]["action"]}</span>
            """)
            label.setAlignment(Qt.AlignCenter)
            yi_layout.addWidget(label)

            reason_label = QLabel()
            reason_label.setText(f"""
                <span style='font-family: 微软雅黑, SimHei, sans-serif;font-size:14px; color:#969696;'>{yi_list[var]["reason"]}</span>
            """)
            reason_label.setAlignment(Qt.AlignCenter)
            yi_layout.addWidget(reason_label)

        # 忌 部分
        seed_str = f"{var1},{var2}"
        random.seed(seed_str)
        var1, var2 = self.get_daily_random_pair(seed_str, 0, len(ji_list) - 1)

        ji_layout = QVBoxLayout()
        ji_layout.setAlignment(Qt.AlignCenter)

        for var in [var1, var2]:
            label = QLabel()
            label.setText(f"""
                <span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:18px; color:#000000;'>忌：</span><!--
             --><span style='font-family: 微软雅黑, SimHei, sans-serif;font-size:18px; color:#000000;'>{ji_list[var]["action"]}</span>
            """)
            label.setAlignment(Qt.AlignCenter)
            ji_layout.addWidget(label)

            reason_label = QLabel()
            reason_label.setText(f"""
                <span style='font-family: 微软雅黑, SimHei, sans-serif;font-size:14px; color:#969696;'>{ji_list[var]["reason"]}</span>
            """)
            reason_label.setAlignment(Qt.AlignCenter)
            ji_layout.addWidget(reason_label)

        # 组合到传入的 layout 中（即 main_layout）
        yi_ji_sublayout = QHBoxLayout()
        yi_ji_sublayout.addLayout(yi_layout)
        yi_ji_sublayout.addLayout(ji_layout)
        layout.addLayout(yi_ji_sublayout)

    def refresh_yi_ji(self):
        # 清空当前“宜/忌”布局中的所有子项
        self.clear_layout(self.yi_ji_layout)
        # 重新加载并设置“宜/忌”
        self.setup_yi_ji_layout(self.yi_ji_layout)

    def clear_layout(self,layout):
        if layout is None:
            return
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())  # 递归清理子布局