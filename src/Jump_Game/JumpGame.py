import os
import sys
#from ctypes import c_long, windll
import platform
from ctypes import c_long
if platform.system() == "Windows":
    from ctypes import windll
import random
import time
from logging import fatal
import math
from random import randint

from PyQt5.QtWidgets import QMainWindow, QGraphicsOpacityEffect, QMessageBox
from _ctypes import Structure, byref

from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QMovie, QPixmap, QRegion


class RECT(Structure):
    _fields_ = [
        ('left', c_long),
        ('top', c_long),
        ('right', c_long),
        ('bottom', c_long)
    ]


def get_taskbar_rect():
    user32 = windll.user32
    hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    if hwnd:
        rect = RECT()
        user32.GetWindowRect(hwnd, byref(rect))
        return (rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)
    return None


class JumpGame(QWidget):
    def __init__(self):
        super().__init__()

        # 窗口设置
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        self.screen_width = screen_geometry.width()
        self.screen_height = screen_geometry.height()
        self.setWindowTitle("PyQt 跳跃游戏")
        self.setFixedSize(self.screen_width, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置窗口位置：放在任务栏正上方
        self.position_window_above_taskbar()

        self.base_path = os.path.dirname(os.path.abspath(__file__))
        # 加载动画资源
        self.run_movie = QMovie(os.path.join(self.base_path, "assets", "whale_gif", "Run.gif"))
        self.jump_movie = QMovie(os.path.join(self.base_path, "assets", "whale_gif", "Jump.gif"))
        self.dive_movie = QMovie(os.path.join(self.base_path, "assets", "whale_gif", "Dive.gif"))

        # 分数系统
        self.score = 0
        self.high_score = self.load_high_score()
        # 分数图像
        self.number_images = [QPixmap(os.path.join(self.base_path, "assets", "numbers", f"{i}.png")) for i in range(10)]
        # 加载 H 和 I 的图像
        self.icon_H = QPixmap(os.path.join(self.base_path, "assets","H.png"))
        self.icon_I = QPixmap(os.path.join(self.base_path, "assets","I.png"))
        # 分数显示容器
        self.score_digits = []
        self.high_score_digits = []
        # 设置位置偏移量
        self.score_label_x = math.ceil(self.screen_width*(2/3))
        self.score_label_y = 200
        self.digit_width = 32  # 根据你的图片大小调整

        #初始化小蓝鲸数据
        self.gravity=0.7
        self.current_movie = self.run_movie
        self.current_movie.setScaledSize(QSize(120, 120))
        self.whale_isjumping = False
        self.whale_isdropping = False
        self.whale_isdiving=False
        self.whale_x = 400
        self.whale_y = 490
        self.whale_vertical_speed = 0
        self.game_start=False
        self.game_over=False
        self.base_jump_force = -10  # 基础跳跃力
        self.max_jump_force = -25  # 最大跳跃力
        self.max_jump_duration = 0.5  # 最大按键时间（秒）
        self.base_drop_force = 50  # 基础下落力
        self.max_drop_force = 100  # 最大下落力
        self.max_drop_duration = 0.5  # 最大按键时间（秒）

        #加载小蓝鲸初始动画
        self.whale_label = QLabel(self)
        self.whale_label.setMovie(self.current_movie)
        self.whale_label.move(self.whale_x, self.whale_y)
        self.current_movie.start()

        #加载海面动画
        self.ocean_movie=QMovie(os.path.join(self.base_path, "assets","ocean.gif"))
        self.ground_label = QLabel(self)
        self.ground_label.setMovie(self.ocean_movie)
        self.ocean_movie.setScaledSize(QSize(self.screen_width, 600))
        # 设置透明度效果（0.0 ~ 1.0）
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.75)  # 75% 透明度
        self.ground_label.setGraphicsEffect(opacity_effect)
        self.ground_label.move(0,50)
        self.ocean_movie.start()
        self.ground_label.show()

        # 计分定时器（每 50ms 加 1 分）
        self.score_timer = QTimer()
        self.score_timer.timeout.connect(self.update_score)

        # 物理引擎定时器（跳跃/下降/重力）
        self.physics_timer = QTimer()
        self.physics_timer.timeout.connect(self.update_physics)

        # 跳跃力计时器
        self.jump_force_timer = QTimer()
        self.jump_force_timer.timeout.connect(self.apply_jump_force_over_time)
        self.space_pressed = False  # 是否正在按下空格键
        self.space_pressed_time = None
        self.jump_force_applied = 0  # 已经应用的跳跃力增量
        self.down_pressed=False #是否正在按下下降键
        self.down_pressed_time=None
        self.drop_force_applied = 0  # 当前已应用的下落力


        #障碍物列表
        self.obstacles = []

        # 障碍物生成定时器
        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_obstacle)
        self.start_time = time.time()

        # 障碍物移动定时器（每帧更新位置）
        self.move_timer = QTimer()
        self.move_timer.timeout.connect(self.move_obstacles)

        #碰撞检测定时器
        self.collision_timer = QTimer()
        self.collision_timer.timeout.connect(self.check_collision)

        # 添加开始提示
        self.start_prompt = QLabel(self)
        self.start_prompt.setAlignment(Qt.AlignCenter)
        self.start_prompt.setText(f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:	#000000;'> 按下空格开始游戏 </span>""")
        self.start_prompt.move(math.ceil(self.screen_width*(1/2))-180, 300)
        self.start_prompt.show()

    def update_score(self):
        if not self.game_over:
            self.score += 1
            self.update_score_display()  # 替换为数字图片显示
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()

    def update_score_display(self):
        for digit in self.score_digits + self.high_score_digits:
            digit.hide()
        self.score_digits.clear()
        self.high_score_digits.clear()

        # 显示当前得分
        score_str = str(self.score)
        total_score_width = len(score_str) * self.digit_width
        start_x = self.score_label_x - total_score_width

        for i, ch in enumerate(score_str):
            idx = int(ch)
            label = QLabel(self)
            pixmap = self.number_images[idx].scaled(QSize(60, 60), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap)
            label.move(start_x + i * self.digit_width, self.score_label_y)
            label.show()
            self.score_digits.append(label)

        # 显示最高得分
        high_score_str = str(self.high_score)
        total_high_score_width = len(high_score_str) * self.digit_width
        start_x_high = self.score_label_x - total_high_score_width

        for i, ch in enumerate(high_score_str):
            idx = int(ch)
            label = QLabel(self)
            pixmap = self.number_images[idx].scaled(QSize(60, 60), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(pixmap)
            label.move(start_x_high + i * self.digit_width, self.score_label_y + 32)
            label.show()
            self.high_score_digits.append(label)

        last_digit_x = start_x_high - 40
        # 显示 H.png（在数字右边）
        label_H = QLabel(self)
        label_H.setPixmap(self.icon_H.scaled(QSize(60, 60), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        label_H.move(last_digit_x - 60, self.score_label_y + 32)
        label_H.show()
        self.high_score_digits.append(label_H)

        # 显示 I.png（在 H.png 右边）
        label_I = QLabel(self)
        label_I.setPixmap(self.icon_I.scaled(QSize(60, 60), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        label_I.move(last_digit_x -60 + self.digit_width, self.score_label_y + 32)
        label_I.show()
        self.high_score_digits.append(label_I)

    def load_high_score(self):
        try:
            with open(os.path.join(self.base_path, "assets","highest_score.txt"), "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        with open(os.path.join(self.base_path, "assets","highest_score.txt"), "w") as f:
            f.write(str(self.high_score))

    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_Space and not self.game_start:
            self.game_start = True
            self.start_prompt.hide()  # 隐藏提示文字
            # 启动所有定时器
            self.score_timer.start(50)
            self.physics_timer.start(11)
            self.jump_force_timer.start(8)
            self.spawn_timer.start(1000)
            self.move_timer.start(8)
            self.collision_timer.start(8)
            self.current_movie.start()  # 开始跑步动画
        if event.key() == Qt.Key_Space and self.game_over:
            self.game_over=False
            self.start_prompt.hide()  # 隐藏提示文字
            # 隐藏并移除所有现存障碍物
            for obs in self.obstacles:
                if 'label' in obs and obs['label']:
                    obs['label'].hide()  # 隐藏 QLabel
                    obs['label'].deleteLater()  # 安全删除 QLabel
            self.obstacles.clear()  # 清空障碍物列表
            self.score=0
            self.start_time=time.time()
            self.score_timer.start(50)
            self.physics_timer.start(11)
            self.jump_force_timer.start(8)
            self.spawn_timer.start(1000)
            self.move_timer.start(8)
            self.collision_timer.start(8)
            self.current_movie.start()  # 开始跑步动画
        if event.key() == Qt.Key_Escape and self.game_over:
            self.deleteLater()
            return
        if (event.key() == Qt.Key_Space or event.key() == Qt.Key_W or event.key() == Qt.Key_Up) and not self.whale_isjumping and not self.whale_isdiving and not self.game_over:
            self.whale_isjumping = True
            self.whale_vertical_speed = self.base_jump_force
            self.current_movie = self.jump_movie
            self.current_movie.setScaledSize(QSize(120, 120))
            self.whale_label.setMovie(self.current_movie)
            self.current_movie.start()
            self.space_pressed = True
            self.space_pressed_time = time.time()
        if (event.key()==Qt.Key_Down or event.key()==Qt.Key_S) and self.whale_isjumping  and not self.game_over and not self.whale_isdropping:
            self.whale_isdropping=True
            self.down_pressed_time=time.time()
        if event.key()==Qt.Key_Down or event.key()==Qt.Key_S:
            self.down_pressed=True



    def keyReleaseEvent(self, event):
        if (event.isAutoRepeat()):
            return
        if event.key() == Qt.Key_Space or event.key() == Qt.Key_W or event.key() == Qt.Key_Up:
            self.space_pressed = False
        if (event.key()==Qt.Key_Down or event.key()==Qt.Key_S):
            self.whale_isdropping=False
            self.down_pressed=False

    def apply_jump_force_over_time(self):
        if self.whale_isjumping and self.space_pressed:
            duration = time.time() - self.space_pressed_time
            # 计算当前应增加的跳跃力(非线性)
            progress = min(duration / self.max_jump_duration, 1)
            desired_force_increase = (self.max_jump_force - self.base_jump_force) * (1 - (1 - progress) ** 2)

            # 只有当新的力比之前大时才更新
            if desired_force_increase < self.jump_force_applied:
                delta = desired_force_increase - self.jump_force_applied
                self.whale_vertical_speed += delta  # 向上更快
                self.jump_force_applied = desired_force_increase

        elif self.whale_isdropping and self.whale_isjumping:
            duration = time.time() - self.down_pressed_time
            progress = min(duration / self.max_drop_duration, 1)
            desired_force_increase = (self.max_drop_force - self.base_drop_force) * (progress ** 2)

            if desired_force_increase > self.drop_force_applied:
                delta = desired_force_increase - self.drop_force_applied
                self.whale_vertical_speed += delta  # 向下更快
                self.drop_force_applied = desired_force_increase



    def update_physics(self):
        ground_level = 490

        if self.whale_isjumping and self.game_over==False:
            self.whale_vertical_speed += self.gravity
            self.whale_y += self.whale_vertical_speed

            if self.whale_y <= ground_level:
                self.whale_label.move(self.whale_x, math.ceil(self.whale_y))

        if self.whale_y >= ground_level and self.down_pressed==True:
            self.whale_isdiving = True
            self.current_movie = self.dive_movie
            self.current_movie.setScaledSize(QSize(120, 120))
            self.whale_label.move(self.whale_x, 520)
            self.whale_label.setMovie(self.current_movie)
            self.current_movie.start()

        if  self.whale_y >= ground_level and self.down_pressed==False:
            # 恢复跑步动画
            self.current_movie = self.run_movie
            self.current_movie.setScaledSize(QSize(120, 120))
            self.whale_label.setMovie(self.current_movie)
            self.whale_vertical_speed = 0
            self.whale_y = ground_level
            self.whale_label.move(self.whale_x, 490)
            self.current_movie.start()
            self.whale_isjumping = False
            self.jump_force_applied = 0  # 重置已应用的力
            self.whale_isdropping = False
            self.drop_force_applied = 0  # 重置已应用的力
            self.whale_isdiving = False


    def check_pixel_collision(self,label1, label2):
        # 获取两个 QLabel 的 QPixmap
        pixmap1 = label1.movie().currentPixmap()
        pixmap2 = label2.pixmap() if label2.pixmap() else (label2.movie().currentPixmap() if label2.movie() else None)

        if not pixmap1 or pixmap1.isNull() or not pixmap2 or pixmap2.isNull():
            return False

        # 获取 mask 并转为 QRegion
        mask1 = pixmap1.mask() if pixmap1.hasAlpha() else None
        mask2 = pixmap2.mask() if pixmap2.hasAlpha() else None

        # 如果没有 mask，默认使用整张图矩形
        region1 = QRegion(mask1) if mask1 else QRegion(pixmap1.rect())
        region2 = QRegion(mask2) if mask2 else QRegion(pixmap2.rect())

        # 移动到 QLabel 的实际位置
        region1.translate(label1.x(), label1.y())
        region2.translate(label2.x(), label2.y())

        # 检查区域是否相交
        return region1.intersects(region2)

    def check_collision(self):
        if self.game_over:
            return

        for obs in self.obstacles:
            obstacle_label = obs['label']
            if self.check_pixel_collision(self.whale_label, obstacle_label):
                self.game_over = True
                self.spawn_timer.stop()
                self.move_timer.stop()
                self.physics_timer.stop()
                self.jump_force_timer.stop()
                self.score_timer.stop()
                self.collision_timer.stop()
                self.start_prompt.setText(
                    f"""<span style='font-family: 微软雅黑, SimHei, sans-serif;font-weight:bold; font-size:36px; color:	#000000;'> 按下空格重新开始|按下ESC退出游戏 </span>""")
                self.start_prompt.move(math.ceil(self.screen_width * (1 / 2)) - 360, 300)
                self.start_prompt.show()
                break

    def  spawn_obstacle(self):
        if(random.randint(1,100)> 30+35*(time.time()-self.start_time)/120):
            return
        obstacle_label = QLabel(self)
        if(time.time()-self.start_time>=30):
            choice=random.randint(1,6)
        else:
            choice=random.randint(1,5)
        ground_level = 490
        if(choice!=6):
            pixmap=QPixmap(os.path.join(self.base_path, "assets","rocks",f"cave_rock{choice}.png"))
            # 缩放图片为宽度固定、高度自适应
            target_width = 100 + math.ceil(100 * random.uniform(0, 1))  # 设置目标宽度
            scaled_pixmap = pixmap.scaledToWidth(target_width, Qt.SmoothTransformation)
            obstacle_label.setPixmap(scaled_pixmap)
            obstacle_height = scaled_pixmap.height()
            start_y = ground_level - obstacle_height + 110  # 确保底部对齐 ground_level
        else:
            movie = QMovie(os.path.join(self.base_path, "assets","bird.gif"))
            movie.setScaledSize(QSize(150, 150))  # 设置大小
            obstacle_label.setMovie(movie)
            movie.start()
            obstacle_height = 150
            start_y= ground_level - obstacle_height + 85 -math.ceil(60*random.uniform(0,1))

        obstacle_label.setAlignment(Qt.AlignBottom | Qt.AlignLeft)

        start_x = self.width() + 10

        obstacle_label.move(start_x, start_y)
        obstacle_label.show()
        obstacle_label.stackUnder(self.ground_label)
        obstacle_speed= 5 + math.ceil(7 * min((time.time() - self.start_time) / 120, 1))
        # 记录障碍物信息
        self.obstacles.append({
            'label': obstacle_label,
            'x': start_x, 
            'y': start_y,
            'width': 40,
            'speed': obstacle_speed
        })

    def move_obstacles(self):
        for obs in self.obstacles:
            obs['x'] -= obs['speed']
            obs['label'].move(obs['x'], obs['y'])

            # 如果障碍物移出屏幕左侧，隐藏并移除
            if obs['x'] < -obs['width']-40:
                obs['label'].hide()
                obs['label'].deleteLater()  #删除 QLabel
                self.obstacles.remove(obs)

    def position_window_above_taskbar(self):
        taskbar_info = get_taskbar_rect()
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = self.width()
        window_height = self.height()

        if taskbar_info:
            taskbar_x, taskbar_y, taskbar_w, taskbar_h = taskbar_info

            if taskbar_y + taskbar_h == screen_height:  # 底部任务栏
                x = (screen_width - window_width) // 2
                y = screen_height - taskbar_h - window_height
            elif taskbar_y == 0:  # 顶部任务栏
                x = (screen_width - window_width) // 2
                y = taskbar_h
            elif taskbar_x == 0:  # 左侧任务栏
                x = taskbar_w
                y = (screen_height - window_height) // 2
            elif taskbar_x + taskbar_w == screen_width:  # 右侧任务栏
                x = screen_width - taskbar_w - window_width
                y = (screen_height - window_height) // 2
            else:
                x, y = 100, 100
        else:
            x, y = 100, 100

        self.move(x, y)
