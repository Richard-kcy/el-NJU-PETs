from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QDialog
from PyQt5.QtCore import Qt, QTimer, QRect


class Ui_Dialog(object):
	def setupUi(self, Dialog):
		Dialog.setObjectName("Dialog")
		Dialog.resize(151, 51)
		Dialog.setStyleSheet("background: transparent;")
		self.pushButton = QtWidgets.QPushButton(Dialog)
		self.pushButton.setGeometry(QtCore.QRect(0, 0, 151, 51))
		font = QtGui.QFont()
		font.setFamily("Microsoft YaHei UI")
		font.setPointSize(10)
		font.setBold(True)
		font.setWeight(75)
		self.pushButton.setFont(font)
		self.pushButton.setFocusPolicy(QtCore.Qt.NoFocus)
		self.pushButton.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
		self.pushButton.setAutoFillBackground(False)
		self.pushButton.setStyleSheet("background-color:white;\n"
"border-style:none;\n"
"padding:8px;\n"
"border-radius:25px;")
		self.pushButton.setObjectName("pushButton")

		self.retranslateUi(Dialog)
		QtCore.QMetaObject.connectSlotsByName(Dialog)

	def retranslateUi(self, Dialog):
		_translate = QtCore.QCoreApplication.translate
		Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
		self.pushButton.setText(_translate("Dialog", "提示框"))



class TipUi(QDialog):
	def __init__(self, text: str, parent=None, parent_pos=None, duration=3):
		# 设置ui
		super().__init__(parent)
		self.parent_pos = parent_pos  # 保存父窗口位置
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)
		# 设置文本
		self.ui.pushButton.setText(text)
		# 计算文本所需尺寸
		self.adjust_size_based_on_text(text)
		# 设置定时器，用于动态调节窗口透明度
		self.timer = QTimer()
		# 显示的文本
		self.ui.pushButton.setText(text)
		# 设置隐藏标题栏、无边框、隐藏任务栏图标
		self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool)
		# 设置窗口透明背景
		self.setAttribute(Qt.WA_TranslucentBackground, True)
		# 窗口关闭自动退出，一定要加，否则无法退出
		self.setAttribute(Qt.WA_QuitOnClose, True)
		# 用来计数的参数
		self.windosAlpha = 0
		# 持续时间配置
		self.total_steps = int(duration * 1000 / 50)  # 计算总步数
		self.windosAlpha = 0

		# 修改定时器连接
		self.timer.timeout.connect(self.hide_windows)
		self.timer.start(50)

	def adjust_size_based_on_text(self, text):
		# 获取字体度量
		font_metrics = self.ui.pushButton.fontMetrics()

		# 分割文本为多行并过滤空行
		lines = [line for line in text.split('\n') if line.strip()]
		if not lines:  # 处理全空行情况
			lines = [""]

		# 计算最长行的宽度
		max_line_width = max(font_metrics.width(line) for line in lines)

		# 计算文本宽度（添加26px边距）
		text_width = max_line_width + 26

		# 计算文本高度（添加10px边距）
		text_height = font_metrics.height() * (1 + text.count('\n')) + 10

		# 设置最小/最大尺寸限制
		max_width = QApplication.desktop().width() // 2
		text_width = min(max(text_width, 100), max_width)  # 宽度在100px到半屏宽之间
		text_height = max(text_height, 40)  # 最小高度40px

		# 调整按钮尺寸
		self.ui.pushButton.setFixedSize(text_width, text_height)

		# 调整窗口尺寸（比按钮大4px用于留白）
		self.setFixedSize(text_width + 4, text_height + 4)

		# 动态设置圆角半径（保持椭圆效果）
		max_radius = 28  # 最大圆角像素
		radius = min(text_height // 2, max_radius)
		self.ui.pushButton.setStyleSheet(f"""
				background-color: white;
				border-style: none;
				padding: 8px;
				border-radius: {radius}px;
			""")

		if self.parent_pos:
			# 计算基于父窗口的位置
			x = self.parent_pos.x() - (self.width() // 2) + 75
			y = self.parent_pos.y() - self.height() - 45
			self.move(x, y)
		else:
			# 默认屏幕底部居中
			screen = QApplication.primaryScreen().availableGeometry()
			self.move(
				int((screen.width() - self.width()) / 2),
				int(screen.height() * 0.85)
			)

	def hide_windows(self):
		self.timer.start(50)
		if self.windosAlpha <= int(self.total_steps * 0.6):  # 前60%时间保持不透明
			self.setWindowOpacity(1.0)
		else:
			# 后40%时间线性淡出
			progress = (self.windosAlpha - int(self.total_steps * 0.6)) / (self.total_steps * 0.4)
			self.setWindowOpacity(1.0 - progress)

		self.windosAlpha += 1
		if self.windosAlpha >= self.total_steps:
			self.close()