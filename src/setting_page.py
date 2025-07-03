import json
import os
import sys

from PyQt5.QtWidgets import (QWidget, QLabel, QComboBox, QVBoxLayout,
                             QHBoxLayout, QPushButton, QMessageBox, QLineEdit, QApplication)
from PyQt5.QtCore import Qt


class SettingPage(QWidget):
    CONFIG_PATH = "user_config.json"  # 配置文件路径

    THEMES = {
        "静谧海洋": {
            "first": "#caf0f8",
            "second": "#90e0ef",
            "third": "#00b4d8",
            "fourth": "#0077b6",
            "background":"#045296"
        },
        "碧海清天": {
            "first": "#c4fff9",
            "second": "#9ceaef",
            "third": "#68d8d6",
            "fourth": "#3dccc7",
            "background":"#07beb8"
        },
        "多氧森林": {
            "first": "#EDECD6",
            "second": "#AAD39C",
            "third": "#4EA770",
            "fourth": "#276F40",
            "background":"#00675f"
        },
        "青翠幽谷":{
            "first": "#dad7cd",
            "second": "#a3b18a",
            "third": "#588157",
            "fourth": "#3a5a40",
            "background":"#344e41"
        },
        "粉黛柔情":{
            "first": "#ffe5ec",
            "second": "#ffc2d1",
            "third": "#ffb3c6",
            "fourth": "#ff8fab",
            "background":"#fb6f92"
        },
        "墨韵清白":{
            "first": "#f2f2f2",
            "second": "#cccccc",
            "third": "#a5a5a5",
            "fourth": "#7f7f7f",
            "background":"#595959"
        },
        "晨曦初照": {
            "first": "#e4b1ab",
            "second": "#e39695",
            "third": "#df7373",
            "fourth": "#da5552",
            "background": "#cc444b"
        }
    }

    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            * {
                font-family: "微软雅黑", "Microsoft YaHei";
            }
        """)
        self.current_location = "nanjing"  # 默认城市
        self.available_locations = {
            "南京": "nanjing",
            "北京": "beijing",
            "上海": "shanghai",
            "广州": "guangzhou",
            "深圳": "shenzhen",
            "杭州": "hangzhou",
            "成都": "chengdu"
        }
        self.api_key = ""  # 新增：存储API密钥
        # 初始化时加载配置
        self.current_location = self._load_config() or "nanjing"  # 优先读取配置
        self.initUI()

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

    def _load_config(self):
        """从配置文件加载保存的城市"""
        base_path=os.path.dirname(os.path.abspath(__file__))
        try:
            if os.path.exists(os.path.join(base_path, self.CONFIG_PATH)):
                with open(os.path.join(base_path, self.CONFIG_PATH), 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.api_key = config.get("api_key", "")  # 新增：加载API密钥
                    return config.get("location", "nanjing")
            return None
        except Exception as e:
            print(f"加载配置失败: {e}")
            return "nanjing"

    def initUI(self):
        theme=self.load_theme()#加载主题
        # 主布局
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(20)

        # +++ 新增API密钥设置区域 +++
        api_group = QWidget()
        api_layout = QVBoxLayout(api_group)
        api_layout.setSpacing(10)

        api_label = QLabel("API密钥设置", self)
        api_label.setStyleSheet("font-size: 18px; color: #555;")
        api_layout.addWidget(api_label)

        # API密钥输入框
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("请输入您的API密钥")
        self.api_key_input.setText(self.api_key)  # 加载已保存的密钥
        self.api_key_input.setEchoMode(QLineEdit.Password)  # 密码模式
        self.api_key_input.setStyleSheet("""
                   QLineEdit {
                       font-size: 16px;
                       padding: 8px;
                       border: 1px solid #ccc;
                       border-radius: 4px;
                   }
               """)
        api_layout.addWidget(self.api_key_input)

        layout.addWidget(api_group)
        # 保存按钮
        save_btn = QPushButton("保存设置", self)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                padding: 8px;
                background-color: {theme["fourth"]};
                color: white;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {theme["third"]};
            }}
        """)
        save_btn.clicked.connect(self.save_api)
        api_layout.addWidget(save_btn)

        # 天气设置区域
        weather_group = QWidget()
        weather_layout = QVBoxLayout(weather_group)
        weather_layout.setSpacing(10)

        weather_label = QLabel("天气城市设置", self)
        weather_label.setStyleSheet("font-size: 18px; color: #555;")
        weather_layout.addWidget(weather_label)

        # 城市选择下拉框
        self.location_combo = QComboBox()
        self.location_combo.addItems(self.available_locations.keys())

        # 设置当前选中项
        current_display = [k for k, v in self.available_locations.items()
                           if v == self.current_location][0]
        self.location_combo.setCurrentText(current_display)

        self.location_combo.setStyleSheet("""
            QComboBox {
                font-size: 16px;
                padding: 5px;
                min-width: 150px;
            }
        """)
        weather_layout.addWidget(self.location_combo)

        # 保存按钮
        save_btn = QPushButton("保存设置", self)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                font-size: 16px;
                padding: 8px;
                background-color: {theme["fourth"]};
                color: white;
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {theme["third"]};
            }}
        """)
        save_btn.clicked.connect(self.save_settings)
        weather_layout.addWidget(save_btn)

        layout.addWidget(weather_group)

        # 主题选择区域
        theme_group = QWidget()
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(10)

        theme_label = QLabel("主题设置", self)
        theme_label.setStyleSheet("font-size: 18px; color: #555;")
        theme_layout.addWidget(theme_label)

        # 主题选择按钮水平布局
        theme_section_layout = QHBoxLayout()

        # 静谧海洋
        ocean_theme_btn = QPushButton("静谧海洋", self)
        ocean_theme_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #0077b6;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00b4d8;
            }
        """)
        ocean_theme_btn.clicked.connect(lambda: self.save_theme("静谧海洋"))
        theme_section_layout.addWidget(ocean_theme_btn)

        #碧海清天
        morning_theme_btn = QPushButton("碧海清天", self)
        morning_theme_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #3dccc7;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #68d8d6;
            }
        """)
        morning_theme_btn.clicked.connect(lambda: self.save_theme("碧海清天"))
        theme_section_layout.addWidget(morning_theme_btn)

        # 多氧森林
        forest_theme_btn = QPushButton("多氧森林", self)
        forest_theme_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #276F40;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4EA770;
            }
        """)
        forest_theme_btn.clicked.connect(lambda: self.save_theme("多氧森林"))
        theme_section_layout.addWidget(forest_theme_btn)

        #青翠幽谷
        chocolate_theme_btn = QPushButton("青翠幽谷", self)
        chocolate_theme_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #3a5a40;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #588157;
            }
        """)
        chocolate_theme_btn.clicked.connect(lambda: self.save_theme("青翠幽谷"))
        theme_section_layout.addWidget(chocolate_theme_btn)

        #粉黛柔情
        melon_theme_btn = QPushButton("粉黛柔情", self)
        melon_theme_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #ff8fab;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ffb3c6;
            }
        """)
        melon_theme_btn.clicked.connect(lambda: self.save_theme("粉黛柔情"))
        theme_section_layout.addWidget(melon_theme_btn)

        # 晨曦初照
        sunrise_theme_btn = QPushButton("晨曦初照", self)
        sunrise_theme_btn.setStyleSheet("""
                    QPushButton {
                        font-size: 16px;
                        padding: 8px;
                        background-color: #da5552;
                        color: white;
                        border: none;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #df7373;
                    }
                """)
        sunrise_theme_btn.clicked.connect(lambda: self.save_theme("晨曦初照"))
        theme_section_layout.addWidget(sunrise_theme_btn)

        #墨韵清白
        beach_theme_btn = QPushButton("墨韵清白", self)
        beach_theme_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                padding: 8px;
                background-color: #7f7f7f;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #a5a5a5;
            }
        """)
        beach_theme_btn.clicked.connect(lambda: self.save_theme("墨韵清白"))
        theme_section_layout.addWidget(beach_theme_btn)


        # 将按钮布局加入主题组
        theme_layout.addLayout(theme_section_layout)

        # 将主题组加入主布局
        layout.addWidget(theme_group)

        self.setLayout(layout)

    def save_theme(self, theme_name):
        """将选中的主题保存到 theme.json"""
        selected_theme = self.THEMES.get(theme_name)
        if not selected_theme:
            print(f"未找到主题: {theme_name}")
            return

        # 构造完整主题结构（可以扩展）
        theme_data = {**selected_theme}

        THEME_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "theme.json")

        try:
            with open(THEME_FILE, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=4)
            QMessageBox.information(self, "主题切换成功",f"主题已切换为{theme_name},重启以生效")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存主题失败: {e}")

    def _save_config(self, location=None, api_key=None):
        """保存配置到文件"""
        base_path=os.path.dirname(os.path.abspath(__file__))
        try:
            # 读取现有配置（如果存在）
            if os.path.exists(os.path.join(base_path, self.CONFIG_PATH)):
                with open(os.path.join(base_path, self.CONFIG_PATH), 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}

            # 只更新传入的参数
            if location is not None:
                config["location"] = location
            if api_key is not None:
                config["api_key"] = api_key

            # 保存完整配置
            with open(os.path.join(base_path, self.CONFIG_PATH), 'w', encoding='utf-8') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def save_settings(self):
        """保存位置设置"""
        selected_city = self.location_combo.currentText()
        self.current_location = self.available_locations[selected_city]

        # 只更新位置信息
        self._save_config(location=self.current_location)

        QMessageBox.information(
            self,
            "设置已保存",
            f"天气城市已设置为: {selected_city}\n设置需要重启生效",
            QMessageBox.Ok
        )

    def save_api(self):
        """保存API密钥设置"""
        # 获取API密钥
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "API密钥不能为空！")
            return

        # 只更新API密钥
        self._save_config(api_key=api_key)

        QMessageBox.information(
            self,
            "设置已保存",
            f"API密钥已更新\n设置需要重启生效",
            QMessageBox.Ok
        )