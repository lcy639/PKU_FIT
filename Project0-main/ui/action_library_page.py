from .base import BasePage
import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QGridLayout, QMenu,
    QPushButton, QMessageBox, QTextEdit, QHBoxLayout, QDialog, QDialogButtonBox,
    QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
class ActionDetailDialog(QDialog):
    def __init__(self, action_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(action_data.get("name", "动作详情"))
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        name_label = QLabel(f"<b>动作名称：</b>{action_data.get('name', '')}")
        layout.addWidget(name_label)

        muscles = ", ".join(action_data.get("target_muscles", []))
        muscles_label = QLabel(f"<b>目标肌肉：</b>{muscles}")
        layout.addWidget(muscles_label)

        equipment_label = QLabel(f"<b>器械：</b>{action_data.get('equipment', '无')}")
        layout.addWidget(equipment_label)

        difficulty_label = QLabel(f"<b>难度：</b>{action_data.get('difficulty', '未知')}")
        layout.addWidget(difficulty_label)

        description_label = QLabel("<b>动作描述：</b>")
        layout.addWidget(description_label)

        description_text = QTextEdit()
        description_text.setReadOnly(True)
        description_text.setText(action_data.get("description", ""))
        layout.addWidget(description_text)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)


class ActionLibraryPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.actions = []
        self.init_ui()
        self.load_actions()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()
        top_layout.addStretch()

        #添加标题
        title_label = QLabel("动作库")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)  # 居中
        main_layout.addWidget(title_label)

        #添加设置按钮
        settings_btn = QPushButton("设置")
        settings_menu = QMenu()
        logout_action = QAction("登出",self)
        settings_menu.addAction(logout_action)
        settings_btn.setMenu(settings_menu)
        logout_action.triggered.connect(self.controller.logout)
        top_layout.addWidget(settings_btn)
        main_layout.addLayout(top_layout)

        #添加动作内容
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(10)

        self.scroll_area.setWidget(self.scroll_content)

        # 返回主页面按钮
        back_btn = QPushButton("返回主页面")
        back_btn.clicked.connect(lambda: self.controller.show_page("MainPage"))
        main_layout.addWidget(back_btn)
        

    def load_actions(self):
        json_path = os.path.join("actions", "fitness_library.json")
        if not os.path.exists(json_path):
            QMessageBox.warning(self, "错误", f"未找到动作库文件：{json_path}")
            return

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                self.actions = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"读取动作库文件失败:\n{e}")
            return

        self.populate_actions()

    def populate_actions(self):
        # 清空旧的内容
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for i, action in enumerate(self.actions):
            name = action.get("name", "未知动作")
            difficulty = action.get("difficulty", "?")

            btn = QPushButton(f"{name}  (难度: {difficulty})")
            btn.setFixedHeight(50)
            btn.clicked.connect(lambda checked, a=action: self.show_detail(a))

            row = i // 2
            col = i % 2
            self.scroll_layout.addWidget(btn, row, col)

    def show_detail(self, action_data):
        dialog = ActionDetailDialog(action_data, self)
        dialog.exec_()
