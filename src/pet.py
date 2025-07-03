import json
import os
import random
from enum import Enum

import bubble
import AIchat
import schedule_page
import requests
from PyQt5.QtCore import Qt, QTimer, QUrl, QPoint, QThread, pyqtSignal
from PyQt5.QtGui import QMovie, QPixmap, QPainter, QColor, QIcon, QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMenu, QAction
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from Jump_Game import JumpGame
from Daily_Fortune.DailyFortune import DailyFortuneWindow
from utils import resource_path
from datetime import datetime

class PetMode(Enum):
    NORMAL = 0
    STUDY = 1
    ENTERTAIN = 2

class MusicLoader(QThread):
    """异步加载音乐文件的线程"""
    loaded = pyqtSignal(dict)  # 信号：传递预加载的音乐路径字典

    def __init__(self, study_folder, rest_folder):
        super().__init__()
        self.study_folder = study_folder
        self.rest_folder = rest_folder
        self.supported_formats = ['.mp3', '.wav']

    def run(self):
        # 预加载学习音乐和休息音乐
        study_files = self._load_folder(self.study_folder)
        rest_files = self._load_folder(self.rest_folder)
        self.loaded.emit({"study": study_files, "rest": rest_files})

    def _load_folder(self, folder_path):
        # 加载单个文件夹中的音乐文件
        if not os.path.exists(folder_path):
            return []
        files = os.listdir(folder_path)
        return [
            os.path.normpath(os.path.join(folder_path, f))
            for f in files
            if os.path.splitext(f)[1].lower() in self.supported_formats
        ]

class DesktopPet(QWidget):
    def __init__(self, mode=PetMode.NORMAL, setting_page=None):
        super().__init__()
        # 设置窗口图标
        self.setWindowIcon(QIcon(resource_path("model/png/pet.png")))
        self.current_mode = mode
        self.setting_page = setting_page  # 保存 SettingPage 实例
        # 定义不同状态下的GIF路径
        self.normal_gif = resource_path("model/gif/start.gif")
        self.study_gif = resource_path("model/gif/study.gif")
        self.rest_gif = resource_path("model/gif/rest.gif")
        self.click_gif = resource_path("model/gif/click.gif")
        self.cry_gif = resource_path("model/gif/cry.gif")
        self.happy_gif = resource_path("model/gif/happy.gif")
        self.anxious_gif = resource_path("model/gif/anxious.gif")
        # 预加载的音乐路径字典
        self.music_cache = {"study": [], "rest": []}
        self.press_pos = QPoint()  # 记录鼠标按下位置
        self.chat_window = None    # 聊天窗口实例
        self.current_mood = None  # 当前心情记录
        self.initUI()  # 初始化界面
        self.initState()  # 初始化状态变量
        self.initMedia()  # 初始化媒体播放器
        self.start_music_preload()  # 启动预加载
        self.schedule_page = schedule_page.SchedulePage()  # 确保初始化
        self.show_startup_interaction()  # 启动时触发问候

    def start_music_preload(self):
        """启动异步音乐预加载"""
        self.loader = MusicLoader(
            study_folder=resource_path("music/study"),
            rest_folder=resource_path("music/rest")
        )
        self.loader.loaded.connect(self.update_music_cache)
        self.loader.start()

    def update_music_cache(self, music_dict):
        """更新音乐缓存"""
        self.music_cache = music_dict
        print("音乐预加载完成！")

    def initUI(self):
        # 窗口基本设置
        self.setFixedSize(150, 150)  # 固定窗口大小
        self.setWindowFlags(  # 设置窗口标志
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint  # 始终置顶
        )
        self.setAttribute(Qt.WA_TranslucentBackground)  # 设置透明背景

        # 创建显示动画的标签
        self.label = QLabel(self)  # 创建QLabel组件
        self.label.setGeometry(0, 0, 150, 150)  # 设置位置和大小

        # 加载动画
        self.loadAnimation(self.normal_gif)

        # 菜单选项创建
        self.study_action = QAction("开始学习模式", self)
        self.quitstudy_action = QAction("退出学习模式", self)
        self.quit_action = QAction("退出程序", self)
        self.schedule_action = QAction("今日日程", self)
        self.game_action = QAction("开始跳跃游戏", self)
        self.fortune_action=QAction("今日运势",self)
        self.weather_action = QAction("查询天气", self)
        self.mood_anaylsis_action = QAction("心情分析", self)

        # 图标
        self.study_action.setIcon(QIcon(resource_path("model/icons/study.png")))
        self.quitstudy_action.setIcon(QIcon(resource_path("model/icons/exit.png")))
        self.quit_action.setIcon(QIcon(resource_path("model/icons/power-off.png")))
        self.schedule_action.setIcon(QIcon(resource_path("model/icons/calendar.png")))
        self.game_action.setIcon(QIcon(resource_path("model/icons/game.png")))
        self.fortune_action.setIcon(QIcon(resource_path("model/icons/fortune.png")))
        self.weather_action.setIcon(QIcon(resource_path("model/icons/weather.png")))
        self.mood_anaylsis_action.setIcon(QIcon(resource_path("model/icons/mood.png")))

        # 创建普通模式菜单
        self.menu1 = QMenu(self)
        self.menu1.setStyleSheet("""
            QMenu {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #d0e7ff;
                color: black;
            }
            QMenu::separator {
                height: 1px;
                background: #ccc;
                margin: 4px 0;
            }
        """)
        font = QFont("微软雅黑", 9, QFont.Normal)
        self.menu1.setFont(font)

        self.menu1.addAction(self.schedule_action)
        self.menu1.addSeparator()
        self.menu1.addAction(self.study_action)
        self.menu1.addSeparator()
        self.menu1.addAction(self.game_action)
        self.menu1.addSeparator()
        self.menu1.addAction(self.mood_anaylsis_action)
        self.menu1.addSeparator()
        self.menu1.addAction(self.fortune_action)
        self.menu1.addSeparator()
        self.menu1.addAction(self.weather_action)
        self.menu1.addSeparator()
        self.menu1.addAction(self.quit_action)

        self.menu1_studying = QMenu(self)
        self.menu1_studying.setStyleSheet("""
            QMenu {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #d0e7ff;
                color: black;
            }
            QMenu::separator {
                height: 1px;
                background: #ccc;
                margin: 4px 0;
            }
        """)
        self.menu1_studying.setFont(font)

        self.menu1_studying.addAction(self.schedule_action)
        self.menu1_studying.addSeparator()
        self.menu1_studying.addAction(self.quitstudy_action)
        self.menu1_studying.addSeparator()
        self.menu1_studying.addAction(self.quit_action)

        # 创建学习模式菜单
        self.menu2 = QMenu(self)
        self.menu1.setStyleSheet("""
            QMenu {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #d0e7ff;
                color: black;
            }
            QMenu::separator {
                height: 1px;
                background: #ccc;
                margin: 4px 0;
            }
        """)
        self.menu2.setFont(font)

        self.menu2.addAction(self.schedule_action)
        self.menu2.addSeparator()
        self.menu2.addAction(self.study_action)
        self.menu2.addSeparator()
        self.menu2.addAction(self.mood_anaylsis_action)
        self.menu2.addSeparator()
        self.menu2.addAction(self.weather_action)
        self.menu2.addSeparator()
        self.menu2.addAction(self.quit_action)

        self.menu2_studying = QMenu(self)
        self.menu2_studying.setStyleSheet("""
            QMenu {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #d0e7ff;
                color: black;
            }
            QMenu::separator {
                height: 1px;
                background: #ccc;
                margin: 4px 0;
            }
        """)
        self.menu2_studying.setFont(font)

        self.menu2_studying.addAction(self.schedule_action)
        self.menu2_studying.addSeparator()
        self.menu2_studying.addAction(self.quitstudy_action)
        self.menu2_studying.addSeparator()
        self.menu2_studying.addAction(self.quit_action)

        #创建娱乐模式菜单
        self.menu3 = QMenu(self)
        self.menu3.setStyleSheet("""
            QMenu {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 6px 24px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #d0e7ff;
                color: black;
            }
            QMenu::separator {
                height: 1px;
                background: #ccc;
                margin: 4px 0;
            }
        """)
        self.menu3.setFont(font)

        self.menu3.addAction(self.game_action)
        self.menu3.addSeparator()
        self.menu3.addAction(self.fortune_action)
        self.menu3.addSeparator()
        self.menu3.addAction(self.mood_anaylsis_action)
        self.menu3.addSeparator()
        self.menu3.addAction(self.weather_action)
        self.menu3.addSeparator()
        self.menu3.addAction(self.quit_action)

        # 连接信号与槽
        self.study_action.triggered.connect(self.startStudy)
        self.quit_action.triggered.connect(self.close)
        self.quitstudy_action.triggered.connect(self.quitStudy)
        self.schedule_action.triggered.connect(self.process_schedules)
        self.game_action.triggered.connect(self.jumpgame)
        self.fortune_action.triggered.connect(self.handle_fortune_click)
        self.weather_action.triggered.connect(self.handle_weather_click)
        self.mood_anaylsis_action.triggered.connect(self.analyze_mood_history_with_ai)

        self.show()  # 显示窗口

    def initState(self):
        # 初始化状态变量
        self.is_learning = False  # 是否处于学习模式
        self.study_phase = 0  # 0-学习阶段 1-休息阶段
        self.cycle_count = 0  # 已完成的学习周期计数
        self.old_pos = QPoint()  # 存储鼠标旧位置
        self.mood_history = []  # 存储带时间的心情记录
        self.load_mood_history()  # 加载历史

    def initMedia(self):
        # 初始化媒体播放器
        self.player = QMediaPlayer()
        self.player.error.connect(self.handle_media_error)  # 连接错误信号
        self.timer = QTimer()
        self.timer.timeout.connect(self.checkState)

    def handle_media_error(self):
        error_msg = self.player.errorString()
        self.showBubble(f"播放错误: {error_msg}")
        print(f"媒体错误详情: {error_msg}")

    def loadAnimation(self, gif_path=None):
        """加载GIF动画（支持动态切换）"""
        if not gif_path:
            gif_path = self.normal_gif  # 默认使用普通模式GIF
        self.movie = QMovie(gif_path)

        if not self.movie.isValid():
            self.showStaticImage()
            return

        self.movie.setScaledSize(self.label.size())  # 调整动画尺寸
        self.label.setMovie(self.movie)  # 将动画设置到标签
        self.movie.start()  # 开始播放动画

    def load_mood_history(self):
        """从本地文件加载带时间戳的心愿记录"""
        history_file = resource_path("src/mood_history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
                    # 确保是列表格式
                    if isinstance(raw_data, list):
                        for item in raw_data:
                            if 'raw_text' not in item:
                                item['raw_text'] = ""  # 添加默认字段
                        self.mood_history = raw_data
                    else:
                        self.mood_history = []
            except Exception as e:
                print(f"加载心情记录失败: {e}")
                self.mood_history = []
        else:
            self.mood_history = []

    def showStaticImage(self):
        # 显示静态图片
        pixmap = QPixmap(resource_path("model/png/pet.png")).scaled(150, 150)  # 加载并缩放图片
        self.label.setPixmap(pixmap)  # 设置到标签

    def showContextMenu(self, pos):
        menu_map = {
            PetMode.NORMAL: self.menu1,
            PetMode.STUDY: self.menu2,
            PetMode.ENTERTAIN: self.menu3
        }
        menu = menu_map.get(self.current_mode, self.menu1)
        if menu == self.menu1 and self.is_learning :
            menu = self.menu1_studying
        if menu == self.menu2 and self.is_learning :
            menu = self.menu2_studying
        menu.exec_(pos)

    def handle_weather_click(self):
        """处理查询天气的点击事件"""
        weather_info = self.get_weather()
        self.ai_weather(weather_info)

    def ai_weather(self,weather_info):
        try:
            # 构造AI提示词
            prompt = f"根据今天天气{weather_info}，这是目前用户的心情：{self.current_mood}，请用可爱的语气给同学介绍天气情况并给与建议，字数不超过20字\n"
            # 创建工作线程
            api_key = self.setting_page.api_key if self.setting_page else ""
            self.ai_worker = AIchat.AIWorker([{
                "role": "user",
                "content": prompt
            }], api_key)
            self.ai_worker.response_received.connect(self._show_weather_bubble)
            self.ai_worker.error_occurred.connect(self.handle_error)  # 连接错误信号
            self.ai_worker.start()
        except Exception as e:
            print(f"AI请求失败: {e}")
            self.showBubble("AI服务暂时不可用")

    def _show_weather_bubble(self, response):
        self.showBubble(response,6)

    def show_startup_interaction(self):
        """启动时问候并获取天气"""
        # 延迟0.5秒后显示问候
        QTimer.singleShot(500, self._show_startup_messages)

    def _show_startup_messages(self):
        """显示问候和天气"""
        # 调用天气API（需自行实现）
        weather = self.get_weather()
        self.showBubble(f"你好呀~ 今天天气{weather}！今天心情怎么样呀？")
        # 延迟1.5秒后弹出输入框
        QTimer.singleShot(1500, self.show_mood_input)

    def get_weather(self):
        """获取实时天气信息"""
        try:
            # API配置
            API_KEY = "SlQUlUirVQXBEqPVd"  # 替换为你的实际密钥
            LOCATION = self.setting_page.current_location if self.setting_page else "nanjing"
            UNIT = "c"                # 温度单位（c-摄氏，f-华氏）
            LANGUAGE = "zh-Hans"      # 简体中文

            # 构造请求URL
            url = f"https://api.seniverse.com/v3/weather/now.json?key={API_KEY}&location={LOCATION}&language={LANGUAGE}&unit={UNIT}"

            # 发送请求（设置2秒超时）
            response = requests.get(url, timeout=2)
            data = response.json()

            # 解析数据
            weather = data["results"][0]["now"]
            return f"{weather['text']}，温度{weather['temperature']}℃"

        except Exception as e:
            print(f"天气获取失败: {e}")
            return "晴朗"  # 默认返回

    def show_mood_input(self):
        """弹出情绪输入对话框"""
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(
            self, "南大小蓝鲸心理小助手", "告诉我你今天的心情吧~（例如：今天阳光真好）"
        )
        if ok and text:
            self.analyze_mood(text)

    def analyze_mood(self, text):
        """调用AI分析情绪"""
        # 构造情绪分析prompt
        prompt = [
            {"role": "system", "content": "请判断用户心情类型，只返回'快乐'、'悲伤'、'焦虑'、'愤怒'、或'平和'中的一个词，不要其他内容。"},
            {"role": "user", "content": f"分析这句话的情绪：{text}"}
        ]
        # 创建工作线程
        api_key = self.setting_page.api_key if self.setting_page else ""
        self.ai_worker = AIchat.AIWorker(prompt, api_key)
        self.ai_worker.raw_text = text  # 保存原始文本供后续使用
        self.ai_worker.response_received.connect(self.handle_mood_response)
        self.ai_worker.error_occurred.connect(self.handle_error)  # 连接错误信号
        self.ai_worker.start()

    def handle_mood_response(self, response):
        """处理情绪分析结果"""
        response = response.strip()
        raw_text = getattr(self.ai_worker, 'raw_text', '')  # 获取原始输入文本

        if response in ["快乐", "悲伤", "焦虑", "愤怒", "平和"]:
            self.current_mood = response
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 当前时间戳
            # 添加带时间戳的记录
            self.mood_history.append({
                "mood": response,
                "raw_text": raw_text,
                "timestamp": timestamp
            })
            if len(self.mood_history) > 10:  # 控制最大记录数量
                self.mood_history.pop(0)
            self.save_mood_history()  # 持久化保存
            self.showBubble(f"检测到你的心情是「{response}」~ 要记得保持好心情哦！")
            if response == "悲伤":
                self.loadAnimation(self.cry_gif)
                QTimer.singleShot(4000,
                                  lambda: (
                                      self.loadAnimation(self.normal_gif),
                                      self.showBubble("别伤心啦！有什么不开心的事可以说给我听呀~")
                                  )
                                  )
            if response == "快乐":
                self.loadAnimation(self.happy_gif)
                QTimer.singleShot(4000,lambda: self.loadAnimation(self.normal_gif))
            if response == "焦虑":
                self.loadAnimation(self.anxious_gif)
                QTimer.singleShot(4000,
                                  lambda: (
                                      self.loadAnimation(self.normal_gif),
                                      self.showBubble("放轻松~有什么烦心事和我说呀~")
                                  )
                                  )
        else:
            self.showBubble("好像没理解你的心情呢...")

    def save_mood_history(self):
        """将带时间戳的心情记录保存到本地文件"""
        history_file = resource_path("src/mood_history.json")
        try:
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(self.mood_history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存心情记录失败: {e}")

    def ai_click(self):
        """调用AI生成问候语"""
        if not self.is_learning :
            # 构造prompt
            prompt = [
                {"role": "user",
                 "content": f"这是目前用户的心情：{self.current_mood}，现在他想与你对话，你要用中文输出一句问候语，少于30字"},
            ]

            # 创建工作线程
            api_key = self.setting_page.api_key if self.setting_page else ""
            self.ai_worker = AIchat.AIWorker(prompt, api_key)

            # 定义响应处理函数
            def handle_response(response):
                # 显示问候语气泡
                self.showBubble(response, duration=3)
                # 延迟1.5秒后打开聊天窗口（保证气泡可见时间）
                QTimer.singleShot(1500, self.open_chat_window)

            # 连接信号
            self.ai_worker.response_received.connect(handle_response)
            self.ai_worker.error_occurred.connect(self.handle_error)  # 连接错误信号
            self.ai_worker.start()

        else :
            self.showBubble("要认真学习哦，有什么学习上的问题欢迎和我一起探讨~")
            # 延迟1.5秒后打开聊天窗口（保证气泡可见时间）
            QTimer.singleShot(1500, self.open_chat_window)

    def handle_error(self, error_msg):
        """显示错误气泡"""
        self.showBubble("AI Error！\n请前往设置页面检查API密钥的可用性\n或检查网络连接状况", 5)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            self.press_pos = event.pos()  # 记录控件相对坐标
            self.dragged = False  # 拖拽标志位
        elif event.button() == Qt.RightButton:
            self.showContextMenu(event.globalPos())

    def mouseReleaseEvent(self, event):
        """处理点击释放事件"""
        if event.button() == Qt.LeftButton:
            # 仅当未发生拖拽且移动距离小于5像素时触发
            if not self.dragged and (event.pos() - self.press_pos).manhattanLength() < 5:
                if not self.is_learning :
                    # 播放点击动画
                    self.loadAnimation(self.click_gif)
                    # 延迟5秒后切换回普通动画
                    QTimer.singleShot(5000, lambda: self.loadAnimation(self.normal_gif))
                    self.ai_click()
                else :
                    self.ai_click()

            # 重置拖拽标志
            self.dragged = False

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # 标记为拖拽操作
            self.dragged = True
            # 计算窗口移动距离
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def open_chat_window(self):
        """打开聊天窗口并传递当前情绪"""
        # 检查窗口是否已存在
        if hasattr(self, 'chat_window') and self.chat_window:
            # 如果窗口存在但被隐藏，则显示它
            if not self.chat_window.isVisible():
                self.chat_window.show()
                self.chat_window.activateWindow()
            return

        try:
            # 导入 ChatWindow 类
            from AIchat import ChatWindow
            # 创建新窗口实例
            self.chat_window = ChatWindow(self)
            # 传递当前情绪到聊天窗口
            self.chat_window.current_mood = self.current_mood
            # 连接信号
            self.chat_window.send_message.connect(self.handle_ai_request)
            self.chat_window.finished.connect(self.close_chat_window)
            # 显示窗口
            self.chat_window.show()
            self.chat_window.activateWindow()
            print("聊天窗口已成功打开")  # 调试信息

        except Exception as e:
            print(f"打开聊天窗口时出错: {e}")
            # 错误处理：显示错误提示
            self.showBubble(f"无法打开聊天窗口: {str(e)}")

    def close_chat_window(self, result):
        """关闭聊天窗口时的清理工作"""
        try:
            if hasattr(self, 'chat_window') and self.chat_window:
                # 断开所有信号连接
                try:
                    self.chat_window.send_message.disconnect()
                except:
                    pass
                try:
                    self.chat_window.finished.disconnect()
                except:
                    pass

                # 关闭并删除窗口
                self.chat_window.close()
                self.chat_window.deleteLater()
                del self.chat_window

            # 重置引用
            self.chat_window = None
        except Exception as e:
            print(f"关闭聊天窗口时出错: {e}")

    def handle_ai_request(self, message):
        """处理AI请求"""
        # 创建工作线程
        api_key = self.setting_page.api_key if self.setting_page else ""
        self.ai_worker = AIchat.AIWorker(message, api_key)
        self.ai_worker.start()

    #跳跃小游戏
    def jumpgame(self):
        self.label.hide()
        self.jump_game = JumpGame.JumpGame()
        self.jump_game.destroyed.connect(lambda: self.game_eval(self.jump_game.score))
        self.jump_game.show()

    #游戏结束，调用AI评价
    def game_eval(self,score):
        self.label.show()
        try:
            # 构造AI提示词
            prompt = f"这是一个类似谷歌小恐龙的游戏,主角是小蓝鲸,1000分以上可以视作是技术较高的玩家,根据游戏分数{score},用诙谐幽默又有点可爱的语气评价游戏成绩,字数不超过20字\n"
            # 创建工作线程
            api_key = self.setting_page.api_key if self.setting_page else ""
            self.ai_worker = AIchat.AIWorker([{
                "role": "user",
                "content": prompt
            }], api_key)
            self.ai_worker.response_received.connect(self._show_eval_bubble)
            self.ai_worker.error_occurred.connect(self.handle_error)  # 连接错误信号
            self.ai_worker.start()
        except Exception as e:
            print(f"AI请求失败: {e}")
            self.showBubble("AI服务暂时不可用")

    #显示游戏评价气泡
    def _show_eval_bubble(self, response):
        self.showBubble(response,6)



    #今日运势
    def handle_fortune_click(self):
        if hasattr(self, 'fortune_window') and self.fortune_window.isVisible():
            return

        self.fortune_window = DailyFortuneWindow(self)
        self.fortune_window.add_button.hide()
        self.fortune_window.exec_()


    # 学习模式控制
    def startStudy(self):
        self.is_learning = True  # 进入学习模式
        self.study_phase = 0  # 设为学习阶段
        self.showBubble("开始专注学习30分钟")  # 显示提示
        self.timer.start(30 * 60 * 1000)  # 启动30分钟定时器
        self.playMusic("study")  # 播放学习音乐
        self.loadAnimation(self.study_gif)  # 切换为学习模式GIF

    def startBreak(self):
        self.study_phase = 1  # 进入休息阶段
        self.cycle_count += 1  # 周期计数+1
        self.showBubble("开始休息5分钟")  # 显示提示
        self.timer.start(5 * 60 * 1000)  # 启动5分钟定时器
        self.playMusic("rest")  # 播放休息音乐
        self.loadAnimation(self.rest_gif)

    def checkState(self):
        # 定时器触发时检查状态
        if self.cycle_count < 3:  # 最多3个周期
            if self.study_phase == 0:
                self.startBreak()  # 学习结束转休息
            else:
                self.startStudy()  # 休息结束转学习
        else:
            self.endStudy()  # 结束学习模式

    def endStudy(self):
        self.timer.stop()  # 停止定时器
        self.player.stop()  # 停止音乐
        self.cycle_count = 0
        self.showBubble("你已经完成一个番茄钟的学习啦！")  # 最终提示
        self.is_learning = False  # 退出学习模式
        self.loadAnimation(self.normal_gif)

    def quitStudy(self):
        self.timer.stop()  # 停止定时器
        self.player.stop()  # 停止音乐
        self.cycle_count = 0
        self.showBubble("退出学习模式")  # 最终提示
        self.is_learning = False  # 退出学习模式
        self.loadAnimation(self.normal_gif)

    def playMusic(self, mode):
        """从缓存中随机播放音乐"""
        # 检查缓存是否为空
        if not self.music_cache.get(mode):
            self.showBubble(f"没有可用的{mode}音乐！")
            return

        # 检查文件路径是否存在
        valid_files = [f for f in self.music_cache[mode] if os.path.exists(f)]
        if not valid_files:
            self.showBubble(f"{mode}音乐文件已丢失！")
            return

        # 随机选择并播放
        music_path = random.choice(valid_files)
        print(f"尝试播放文件: {music_path}")  # 调试输出
        media = QMediaContent(QUrl.fromLocalFile(music_path))
        self.player.setMedia(media)
        self.player.play()

    def showBubble(self, text, duration=3):
        # 调用气泡组件
        pet_center = self.mapToGlobal(QPoint(75, 75))
        self.bubble = bubble.TipUi(
            text,
            parent=self,
            parent_pos=pet_center,
            duration=duration  # 传递持续时间
        )
        self.bubble.show()

    def closeEvent(self, event):
        """窗口关闭时自动调用"""
        if self.is_learning:
            self.quitStudy()
        if self.chat_window:
            self.chat_window.close()  # 关闭聊天窗口（如果存在）
        event.accept()  # 确认关闭

    def process_schedules(self):
        """处理日程查询请求"""
        try:
            # 获取今日日程
            today_schedules = self.schedule_page.get_today_schedules()

            if today_schedules:
                self.showBubble("南大小蓝鲸助手正在帮你整理日程中~")
                self._ask_ai_schedules(today_schedules, "今日")
            else:
                self.showBubble("今日没有日程安排哦~")
        except Exception as e:
            print(f"日程处理错误: {e}")
            self.showBubble("日程查询失败，请检查数据")

    def _ask_ai_schedules(self, schedules, date_label):
        """调用AI处理日程"""
        try:
            # 构造AI提示词
            prompt = f"请用可爱简短的语气整理{date_label}的日程：\n"
            for idx, s in enumerate(schedules, 1):
                prompt += f"{idx}. 时间：{s['time']} 标题：{s['title']} 详情：{s['detail']}\n"
            prompt += f"用中文回复，一行不要太长（可以换行），总日程不要超过150字，用波浪号结尾~这是目前用户的心情：{self.current_mood}"

            # 创建工作线程
            api_key = self.setting_page.api_key if self.setting_page else ""
            self.ai_worker = AIchat.AIWorker([{
                "role": "user",
                "content": prompt
            }], api_key)
            self.ai_worker.response_received.connect(self._show_schedule_bubble)
            self.ai_worker.error_occurred.connect(self.handle_error)  # 连接错误信号
            self.ai_worker.start()
        except Exception as e:
            print(f"AI请求失败: {e}")
            self.showBubble("AI服务暂时不可用")

    def _show_schedule_bubble(self, response):
        """显示日程气泡"""
        self.showBubble(response, 8)

    def analyze_mood_history_with_ai(self):
        """调用AI分析所有心情记录"""
        if not self.mood_history:
            self.showBubble("还没有心情记录哦~")
            return

        self.showBubble("南大小蓝鲸助手正在分析心情记录中~")
        # 构造分析内容
        prompt = [
            {
                "role": "system",
                "content": "你是一个心理助手，请根据用户提供的历史心情记录，先总结他近期的情绪变化，然后简单分析他的情绪，并给出建议。输出语言要亲切可爱，可以换行，每行字数不超过30字。"
            },
            {
                "role": "user",
                "content": self._format_mood_history_for_prompt()
            }
        ]

        api_key = self.setting_page.api_key if self.setting_page else ""
        self.ai_worker = AIchat.AIWorker(prompt, api_key)
        self.ai_worker.response_received.connect(lambda response: self.showBubble(response, 10))
        self.ai_worker.error_occurred.connect(self.handle_error)
        self.ai_worker.start()

    def _format_mood_history_for_prompt(self):
        """将心情历史格式化为AI可理解的文本"""
        lines = []
        for idx, record in enumerate(self.mood_history, 1):
            lines.append(f"{idx}. [{record['timestamp']}] {record['mood']}：[{record['raw_text']}]")
        return "\n".join(lines)