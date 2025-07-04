# NJU-PETs ——— 南大人自己的智能桌宠 
![小蓝鲸桌宠截图](model/gif/start.gif)    
*“用代码传递温情 ”*

## 🌟 项目简介  
**NJU-PETs** 项目灵感来自于大学校园中普遍存在的高压学习节奏与孤独情绪。我们希望通过一个结合 **成长助手** 与 **心灵伙伴** 功能的智能桌宠，为同学们提供情绪陪伴、任务管理与趣味互动体验。  

桌宠“小蓝鲸”不仅具备可爱的视觉形象，还能与用户进行对话、游戏、提醒与安慰，是一款有温度的代码作品，项目目标是开发一款具备实用性与趣味性的桌宠系统，涵盖学习管理、心理交互与日常陪伴三大功能场景

### 项目成员
**不用Debug都队**：柯承佑 巨文博 蒲今 王天宇 

---

## 🚀 快速开始

### 环境要求
- 系统：Windows

### 安装前
- [点击此处下载完整项目压缩包](https://1drv.ms/u/c/3fee49f8f537c168/EfkCfcBNO6FJj0Q8Y2ysydYBUG_a9G0nE-mWdXLHiQV2-g?e=YIwB15)
> ⚠️ 注意：由于 GitHub 文件大小限制，本仓库未包含 `.gif` 动画与 `.mp3` 音频等大文件，完整资源请通过上方链接下载。
- 在gitlab右侧项目信息处点击【发布】跳转后下载【软件包】 (NJU-PETs-setup.exe) 并根据引导安装 NJU-PETs(**不要装在C盘**)
- 需要获取AI对话的api-key（在阿里云百炼平台可申请）
- ~~需要获取天气api-key~~（目前不需要）

### 启动后
- 在设置页面中填入你的api-key并选择你的地区（默认南京）（填写后需要**重启**以加载配置）
- 在启动页面选择模型和模式（模式分普通模式、学习模式、娱乐模式，其中普通模式具有所有功能）

### 详细交互
#### 面板设置
- 运行程序后的初始界面
- 日程板块及其曾删查改
- 设置——ai密钥和城市选择
- 更多——今日运势、帮助文档、关于我们和项目仓库
#### 生成自定义小蓝鲸
- 模型选择（目前仅有小蓝鲸）
- 模式选择（有普通模式、学习模式和娱乐模式）
- 运行之后报告天气和询问心情
- 小蓝鲸的外形依据心情变化
#### 小蓝鲸功能
###### 以下以普通模式的功能举例（普通模式包含所有功能）
- 功能一：左键，唤出ai对话框（ai带有心情和日程的记忆）
- 功能二：今日日程
- 功能三：开始学习模式（娱乐模式无此功能）
- 功能四：开始跳跃模式（学习模式无此功能）
- 功能五：今日运势
- 功能六：查询天气
- 功能七：心情分析

---

## ✨ 功能亮点  
### 情绪化AI交互  
- 接入大语言模型（阿里云百炼API），识别用户心情关键词并动态调整对话风格。  
- 启动时主动问候，引导用户输入情绪状态（如“有点累”“挺开心”）。

### 专注学习模式  
- 内置番茄钟逻辑，自动计时三轮学习（30分钟）与休息（5分钟）。  
- 支持雨声、海浪声等环境音，提升学习专注力。  

### 趣味娱乐模块  
- **JumpGame 小游戏**：控制小蓝鲸跳跃/下蹲躲避障碍物，游戏难度随着时间增加，实时分数记录与历史最高分展示。  
- **今日运势**：生成学习、社交、debug等趣味运势（仿洛谷风格）。  

### 便捷工具集成  
- **天气提示**：接入心知天气API，自动获取南京（默认）或其他城市天气信息。  
- **日程管理**：支持签到打卡、任务规划，数据本地持久化存储。  
- **音乐播放**：支持 `.mp3` 和 `.wav` 格式，用户可自定义背景音乐。

---

## 🔧 开发说明
### 技术栈
1. **核心语言**：Python

2. **图形界面**：PyQt5（QStackedWidget 管理多页面，QMovie 播放动画）

3. **AI 模块**：使用阿里云百炼api-key（异步请求由 QThread 处理）

4. **数据存储**：本地 JSON 文件（任务记录、API 配置等）

5. **游戏逻辑**：2D 物理引擎（重力模拟、像素级碰撞检测）

6. **动画制作**：Adobe After Effects、Quicktime、Adobe PhotoShop、Adobe Premiere 

### 关键实现细节
1. **动画系统**：通过 QPixmap 加载透明 GIF，动态调整小蓝鲸表情与动作。

2. **游戏物理**：跳跃加速度、下落速度曲线、障碍物随机生成与动态难度。

3. **音乐播放**：自动识别 music 文件夹中的音频文件，按模式随机播放。

### 文件结构
```  
src
|-- AIchat.py
|-- bubble.py
|-- controller.py
|-- Daily_Fortune
|   |-- DailyFortune.py
|   `-- EditFortunes.py
|-- Jump_Game
|   |-- assets
|   |   |-- numbers
|   |   |-- rocks
|   |   `-- whale_gif
|   `-- JumpGame.py
|-- main.py
|-- more_page.py
|-- panel.py
|-- pet.py
|-- schedule_page.py
|-- setting_page.py
`-- utils.py
model
|-- gif
|-- icons
`-- png
music
|-- rest
`-- study
docs
|-- help.html
`-- about.html
packages.txt
```

### 项目模块
![项目模块截图](model/png/xiangmumokuai.png) 

### 模块概要
#### 模块一  启动与控制模块
由 main.py 和 controller.py 组成，负责系统的启动、窗口初始化和各功能之间的统一调度。
#### 模块二  用户界面模块
包括 panel.py、schedule_page.py、setting_page.py 和 more_page.py，负责构建各页面界面，实现用户操作的交互界面展示。
#### 模块三  核心业务模块
包含桌宠行为控制（pet.py）、AI 聊天功能（AIchat.py）、气泡提示（bubble.py）等，是系统主要功能的实现部分。
#### 模块四  日程模块
由 schedule_page.py 和 schedules.json 组成，支持用户添加、编辑和查看日常任务，实现基本的日程管理功能。
#### 模块五  数据与资源模块
数据文件包括 user_config.json、checkin_record.json 等，资源目录包含 model/ 和 music/，用于存储配置、状态、图像和音频素材，支撑系统的持续运行与表现力。
#### 模块六  附加功能模块
包括 Daily_Fortune/ 和 Jump_Game/ 两个子系统，分别实现每日签到与运势功能、跳跃类小游戏，增强系统趣味性与互动性。

---

### 👥 开发者介绍
| 成员   | 分工                                      |
|--------|-----------------------------------------|
| 柯承佑 | UI 设计、桌宠逻辑与部分调试优化                       |
| 巨文博 | JumpGame 小游戏实现、今日运势模块、UI 动画制作与部分调试优化    |
| 蒲今   | 美工、桌宠逻辑、日程系统、天气分析系统、AI 对话及情绪分析系统与部分调试优化 |
| 王天宇 | 桌宠角色美术设计结合 AE 动画制作、动画整合与界面调试优化          |

---

### 📚 参考资料模块
- **PyQt5 帮助文档**  
  [https://doc.qt.io/qtforpython/modules.html](https://doc.qt.io/qtforpython/modules.html) 

- **OpenAI API 文档**  
  [https://platform.openai.com/docs](https://platform.openai.com/docs)

- **阿里云百炼平台**  
  [https://bailian.aliyun.com](https://bailian.aliyun.com)

- **Adobe After Effects 使用手册**  
  [https://helpx.adobe.com/after-effects/user-guide.html](https://helpx.adobe.com/after-effects/user-guide.html)

- **洛谷今日运势源码参考**  
  [https://github.com/luogu-dev/fortune](https://github.com/luogu-dev/fortune)   

- **GitLab CI/CD 与协作开发指南**  
  [https://docs.gitlab.com/ee/user/project/](https://docs.gitlab.com/ee/user/project/)

---

### 🌱 未来计划模块
1. **学习功能增强**  
   - 引入 AI 主动学习辅助机制，结合费曼学习法提问与知识回顾。  
   - 基于艾宾浩斯遗忘曲线自动生成复习计划与提醒，提升记忆效率。  

2. **角色与生态扩展**  
   - 构建多角色生态系统（如“学术型”“搞笑型”），支持不同语气风格与行为逻辑。  
   - 精细化动画表现（打哈欠、困倦趴下等），实现情绪与动作自然过渡。  
   - 开放用户皮肤系统与社区共享机制，支持自定义角色与内容生态。
   - 集成语音输入与语音合成，实现真正“说话+听话”的自然人机对话；成为可嵌入多任务工作流中的智能界面。

3. **交互升级**  
   - 集成语音输入与语音合成功能，实现自然语音对话。  
   - 开放 API 与插件支持，拓展多任务工作流嵌入能力。  

4. **功能深化**  
   - 优化番茄钟逻辑，支持自定义学习/休息时长与循环次数。  
   - 增加更多小游戏模块与动态难度调节机制。  

---

### 🙏 特别鸣谢
 感谢以下同学为本项目提供了测试意见：
 - 陈晴柔
 - 蔡子奇
 - 陆亭羽
 - 徐黄浩
 - 傅俊杰
 - 戴坤雨

> **团队**: 不用Debug都队 NoDebug Team | **开源地址**: https://git.nju.edu.cn/Benzoic/el-project-nodebug.git   
> 用代码传递温情，让学习不再孤单，让效率触手可及 🐋
