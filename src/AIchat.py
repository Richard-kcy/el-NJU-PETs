import json
import os
from PyQt5.QtCore import pyqtSignal, Qt, QThread, QMutex, QPoint
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QTextBlockFormat, QColor
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QApplication, QDesktopWidget, QScrollBar, QLabel
)
from openai import OpenAI


class ChatWindow(QDialog):
    send_message = pyqtSignal(str)
    MAX_HISTORY = 5  # 保留最近5条对话

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mood = None  # 情绪状态存储
        self.parent_pet = parent  # 保存父级引用
        self.init_ui()
        self.ai_worker = None
        self.history = []  # 对话历史存储
        self.history_lock = QMutex()  # 线程安全锁
        self.setWindowTitle("南大小蓝鲸助手")
        self.thinking_message_pos = None

        # 使用标准窗口标志
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint |
                            Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        # 简化样式表
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f8ff;
                border: 1px solid #c0d6e4;
                border-radius: 15px;
            }
            QLineEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 15px;
                padding: 8px 12px;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #4a9cff;
                color: white;
                border-radius: 15px;
                font-weight: bold;
                padding: 8px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #6ab0ff;
            }
        """)

    def init_ui(self):
        # 移除固定大小设置，改为设置最小尺寸
        self.setMinimumSize(450, 570)

        # 布局
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # 聊天记录区域 - 添加拉伸因子
        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setStyleSheet("""
                    QTextEdit {
                        background-color: #ffffff;
                        border-radius: 10px;
                        padding: 11px;
                        font-size: 11pt;
                        border: 1px solid #ddd;
                    }
                """)
        # 添加拉伸因子，使聊天区域可以随窗口缩放
        layout.addWidget(self.chat_log, 1)  # 参数1表示拉伸因子

        # 输入区域
        input_layout = QVBoxLayout()

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("输入消息...")
        self.input_box.returnPressed.connect(self.send_clicked)
        input_layout.addWidget(self.input_box)

        # 发送按钮
        self.send_btn = QPushButton("发送")
        self.send_btn.clicked.connect(self.send_clicked)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)
        self.setLayout(layout)
        self.center_window()
        # 添加欢迎消息
        self.add_message("NJU-Pet", "你好呀！我是南大小蓝鲸助手，有什么我可以帮你的吗？", is_pet=True)

    def center_window(self):
        """窗口居中显示"""
        screen = QDesktopWidget().screenGeometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def show(self):
        """确保窗口正确显示"""
        super().show()
        self.activateWindow()  # 激活窗口
        self.raise_()  # 置于顶层
        QApplication.processEvents()  # 处理待处理事件

    def send_clicked(self):
        """发送消息处理"""
        text = self.input_box.text()
        if text.strip():
            self._add_to_history("user", text)
            self.add_message("You", text, is_user=True)
            self.send_message.emit(text)
            self.input_box.clear()
            self.process_ai_message(text)

    def add_message(self, sender, message, is_user=False, is_pet=False):
        """添加消息到聊天记录 - 使用格式化的文本"""
        # 创建文本格式
        char_format = QTextCharFormat()
        block_format = QTextBlockFormat()
        block_format.setTopMargin(5)
        block_format.setBottomMargin(5)

        # 设置消息格式
        if is_user:
            block_format.setBackground(QColor("#e0f7fa"))  # 浅蓝色背景
            block_format.setAlignment(Qt.AlignRight)  # 右对齐
        elif is_pet:
            block_format.setBackground(QColor("#f5f5f5"))  # 浅灰色背景
            block_format.setAlignment(Qt.AlignLeft)  # 左对齐

        # 添加发送者名称
        cursor = self.chat_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        start_pos = cursor.position()
        cursor.insertBlock(block_format)
        cursor.setCharFormat(char_format)
        cursor.insertHtml(f"<b>{sender}</b><br>")

        # 添加消息内容
        cursor.setCharFormat(char_format)  # 确保内容也使用相同的格式
        cursor.insertHtml(message.replace("\n", "<br>"))

        # 添加分隔线
        cursor.setCharFormat(QTextCharFormat())
        cursor.insertHtml("<hr>")

        end_pos = cursor.position()

        # 滚动到底部
        self.chat_log.ensureCursorVisible()
        cursor.movePosition(QTextCursor.End)
        self.chat_log.setTextCursor(cursor)

        # 返回消息ID（当前块位置）
        return (start_pos, end_pos)

    def process_ai_message(self, message):
        """启动AI处理"""
        # 添加"正在思考"消息并记录ID
        self.thinking_message_pos = self.add_message("NJU-Pet", "正在思考中...", is_pet=True)

        # 获取当前对话历史
        self.history_lock.lock()
        messages = self._format_messages()
        self.history_lock.unlock()

        # 从父级获取API密钥
        api_key = ""
        if self.parent_pet and hasattr(self.parent_pet, 'setting_page'):
            api_key = self.parent_pet.setting_page.api_key

        # 创建worker时传入完整对话历史和密钥
        self.ai_worker = AIWorker(messages, api_key)
        self.ai_worker.response_received.connect(self.handle_ai_response)
        self.ai_worker.error_occurred.connect(self.handle_ai_error)
        self.ai_worker.start()

    def handle_ai_response(self, response):
        """处理AI响应并保存到历史"""
        # 移除"正在思考中..."消息
        self.remove_thinking_message()

        # 添加AI回复
        self.add_message("NJU-Pet", response, is_pet=True)
        self._add_to_history("assistant", response)

    def handle_ai_error(self, error_msg):
        """处理AI错误"""
        # 移除"正在思考中..."消息
        self.remove_thinking_message()

        # 显示错误消息
        self.add_message("NJU-Pet", f"出错了: {error_msg}", is_pet=True)

    def remove_thinking_message(self):
        """移除'正在思考中...'消息"""
        if self.thinking_message_pos is not None:
            start_pos, end_pos = self.thinking_message_pos
            cursor = self.chat_log.textCursor()

            # 选择整个消息范围
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)

            # 删除整个消息
            cursor.removeSelectedText()

            self.thinking_message_pos = None

    def _format_messages(self):
        """将历史转换为API需要的格式（始终以系统消息开头）"""
        mood_prompt = f"用户当前心情状态为：{self.current_mood}\n" if self.current_mood else ""

        system_message = {
            "role": "system",
            "content": f"""你需要根据用户心情调整回应方式。{mood_prompt}
                    如果有人问你你是谁，你要说你是南大小蓝鲸助手。回答要简短且符合当前对话情境。"""
        }
        # 转换历史记录
        history_messages = [
            {
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["content"]
            } for msg in self.history
        ]

        return [system_message] + history_messages

    def _add_to_history(self, role, content):
        """线程安全添加对话记录"""
        self.history_lock.lock()
        self.history.append({"role": role, "content": content})

        # 保持历史记录长度
        if len(self.history) > self.MAX_HISTORY * 2:
            self.history = self.history[-self.MAX_HISTORY * 2:]
        self.history_lock.unlock()

class AIWorker(QThread):
    """AI 工作线程"""
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, messages, api_key):
        super().__init__()
        self.messages = messages
        self.api_key = api_key

    def run(self):
        try:
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            completion = client.chat.completions.create(
                model="qwen-plus",
                messages=self.messages,
                extra_body={"enable_thinking": False},
            )
            self.response_received.emit(completion.choices[0].message.content)
        except Exception as e:
            error_msg = self._parse_error(e)
            self.error_occurred.emit(error_msg)

    def _parse_error(self, e):
        """错误信息分类处理"""
        if "400" in str(e) and "json_object" in str(e):
            return "请求格式错误，请联系开发者"
        else:
            self.error_occurred.emit("error")  # 发送错误信号