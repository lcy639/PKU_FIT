from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QMenu, QAction, QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class MainPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 顶部布局
        top_layout = QHBoxLayout()
        top_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))

        # 设置按钮
        settings_btn = QPushButton("设置")
        settings_menu = QMenu()
        view_history_action = QAction("查看历史记录", self)
        logout_action = QAction("登出", self)
        settings_menu.addAction(view_history_action)
        settings_menu.addAction(logout_action)
        settings_btn.setMenu(settings_menu)
        top_layout.addWidget(settings_btn)

        # 设置事件
        view_history_action.triggered.connect(lambda: self.controller.show_page("ViewPage"))
        logout_action.triggered.connect(lambda: self.controller.logout())

        main_layout.addLayout(top_layout)

        # 中部区域（可添加饼图等）
        center_label = QLabel("（这里将放置健身房人数饼状图）")
        center_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(center_label)

        # 底部按钮布局
        bottom_layout = QHBoxLayout()

        # 按钮 1：动作库
        action_lib_btn = QPushButton("动作库")
        action_lib_btn.setIcon(QIcon("assets/action_lib.png"))  # 可替换成你图片路径
        action_lib_btn.clicked.connect(self.show_action_library)

        # 按钮 2：个性化动作
        custom_action_btn = QPushButton("个性化动作")
        custom_action_btn.setIcon(QIcon("assets/custom_action.png"))
        custom_action_btn.clicked.connect(self.show_custom_action_options)

        # 按钮 3：身体数据
        body_data_btn = QPushButton("身体数据")
        body_data_btn.setIcon(QIcon("assets/body_data.png"))
        body_data_btn.clicked.connect(self.show_body_data_placeholder)

        # 添加到底部布局
        bottom_layout.addWidget(action_lib_btn)
        bottom_layout.addWidget(custom_action_btn)
        bottom_layout.addWidget(body_data_btn)

        main_layout.addLayout(bottom_layout)

    def show_action_library(self):
        QMessageBox.information(self, "动作库", "这里将展示动作库内容")

    def show_custom_action_options(self):
        QMessageBox.information(self, "个性化动作", "这里将提供自动或自选训练方案")

    def show_body_data_placeholder(self):
        QMessageBox.information(self, "身体数据", "这里将展示身体数据页面")
