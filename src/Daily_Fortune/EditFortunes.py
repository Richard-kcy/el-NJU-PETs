from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, \
    QLabel, QMessageBox


class EditFortuneDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("编辑提示词")
        self.data = data or {
            "yi": [],
            "ji": []
        }
        self.current_type = "yi"
        self.current_item = None  # 当前选中的列表项
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # 类型选择
        type_layout = QHBoxLayout()
        self.yi_btn = QPushButton("宜")
        self.ji_btn = QPushButton("忌")

        self.yi_btn.clicked.connect(lambda: self.switch_type("yi"))
        self.ji_btn.clicked.connect(lambda: self.switch_type("ji"))

        type_layout.addWidget(self.yi_btn)
        type_layout.addWidget(self.ji_btn)
        layout.addLayout(type_layout)

        # 列表显示
        self.list_widget = QListWidget()
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)

        # 动作和理由输入
        self.action_input = QLineEdit()
        self.reason_input = QLineEdit()
        layout.addWidget(QLabel("动作："))
        layout.addWidget(self.action_input)
        layout.addWidget(QLabel("理由："))
        layout.addWidget(self.reason_input)

        # 按钮
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("修改")
        self.add_btn = QPushButton("新增")
        self.delete_btn = QPushButton("删除")

        self.save_btn.clicked.connect(self.save_item)
        self.add_btn.clicked.connect(self.add_item)
        self.delete_btn.clicked.connect(self.delete_item)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.switch_type("yi")  # 初始化为标题

    def switch_type(self, fort_type):
        self.current_type = fort_type
        self.list_widget.clear()
        items = self.data.get(fort_type, [])
        for item in items:
            list_item = QListWidgetItem(item["action"])
            list_item.setData(Qt.UserRole, item)  # 存储完整数据
            self.list_widget.addItem(list_item)
        self.current_item = None  # 清空当前选中项
        self.action_input.clear()
        self.reason_input.clear()
        self.update_button_state()

    def on_selection_changed(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            self.current_item = selected_items[0]
            item_data = self.current_item.data(Qt.UserRole)
            self.action_input.setText(item_data["action"])
            self.reason_input.setText(item_data["reason"])
        else:
            self.current_item = None
            self.action_input.clear()
            self.reason_input.clear()
        self.update_button_state()

    def update_button_state(self):
        has_selection = self.current_item is not None
        self.save_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

    def save_item(self):
        if not self.current_item:
            return

        action = self.action_input.text().strip()
        reason = self.reason_input.text().strip()

        if not action or not reason:
            QMessageBox.warning(self, "错误", "请输入完整内容！")
            return

        item_data = self.current_item.data(Qt.UserRole)
        item_data["action"] = action
        item_data["reason"] = reason
        index = self.list_widget.row(self.current_item)
        self.data[self.current_type][index] = item_data
        QMessageBox.information(self, "成功", "内容已修改！")
        self.switch_type(self.current_type)


    def add_item(self):
        action = self.action_input.text().strip()
        reason = self.reason_input.text().strip()

        if not action or not reason:
            QMessageBox.warning(self, "错误", "请输入完整内容！")
            return

        new_item = {"action": action, "reason": reason}
        for item in self.data[self.current_type]:
            if item["action"] == action:
                QMessageBox.warning(self, "提示", "已存在相同动作")
                return

        self.data[self.current_type].append(new_item)
        list_item = QListWidgetItem(action)
        list_item.setData(Qt.UserRole, new_item)
        self.list_widget.addItem(list_item)
        self.action_input.clear()
        self.reason_input.clear()
        QMessageBox.information(self, "成功", "已新增内容！")

    def delete_item(self):
        if not self.current_item:
            return

        reply = QMessageBox.question(self, "确认", "确定要删除此项吗？")
        if reply == QMessageBox.Yes:
            if len(self.data[self.current_type])==2:
                QMessageBox.warning(self, "提示", "至少需要含有两个提示词")
                return
            row = self.list_widget.row(self.current_item)
            self.list_widget.takeItem(row)
            del self.data[self.current_type][row]
            self.current_item = None
            self.action_input.clear()
            self.reason_input.clear()
            self.update_button_state()
            QMessageBox.information(self, "成功", "已删除内容！")

    def mousePressEvent(self, event):
        # 获取点击位置相对于 list_widget 的矩形区域
        pos = event.pos()
        rect = self.list_widget.geometry()

        # 判断是否点击在 list_widget 区域内
        if not rect.contains(pos) and self.current_item is not None:
            self.list_widget.clearSelection()
            self.current_item = None
            self.action_input.clear()
            self.reason_input.clear()
            self.update_button_state()

        super().mousePressEvent(event)