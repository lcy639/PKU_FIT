from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QScrollArea, QFrame, QMenu, QAction, QSpacerItem, QSizePolicy, QGridLayout, QMessageBox
)
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from data_interface.datamanager import TrainingInfo

class CardButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(parent)
        self.setFixedSize(180, 100)
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #aaa;
                border-radius: 8px;
                background-color: #fefefe;
                text-align: center;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e6f0ff;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        if icon_path:
            icon_label = QLabel(self)
            pixmap = QPixmap(icon_path)
            pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)

        text_label = QLabel(text, self)
        text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(text_label)

        self.setLayout(layout)


class MainPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.selected_actions = []  # 这里存储所有已添加动作（包括重复）
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 顶部设置按钮
        top_layout = QHBoxLayout()
        top_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))

        settings_btn = QPushButton("设置")
        settings_menu = QMenu()
        logout_action = QAction("登出", self)
        settings_menu.addAction(logout_action)
        settings_btn.setMenu(settings_menu)
        logout_action.triggered.connect(self.controller.logout)
        top_layout.addWidget(settings_btn)
        main_layout.addLayout(top_layout)

        # 中部布局：左侧清单 + 中间动作列表
        center_layout = QHBoxLayout()

        # 左侧布局（包含清单和保存按钮）
        left_layout = QVBoxLayout()

        self.selected_list = QListWidget()
        self.selected_list.setFixedWidth(200)
        left_layout.addWidget(self.selected_list)

        # 保存按钮
        save_btn = QPushButton("保存动作清单")
        save_btn.clicked.connect(self.save_selection)

        left_layout.addWidget(save_btn)

        # 新增：删除按钮
        delete_btn = QPushButton("删除选中动作")
        delete_btn.clicked.connect(self.delete_selected_action)

        left_layout.addWidget(delete_btn)

        center_layout.addLayout(left_layout)

        # 中间：可滚动的动作列表
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QGridLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(5, 5, 5, 5)

        self.exercise_data = [
            ("深蹲", "images/squat.png"),
            ("俯卧撑", "images/push_up.png"),
            ("硬拉", "images/deadlift.png"),
            ("引体向上", "images/pull_up.png"),
            ("卷腹", "images/crunch.png"),
            ("哑铃肩推", "images/dumbbell_shoulder_press.png"),
            ("哑铃弯举", "images/dumbbell_curl.png"),
            ("杠铃卧推", "images/barbell_bench_press.png"),
            ("俄罗斯转体", "images/russian_twist.png"),
            ("坐姿腿屈伸", "images/leg_extension.png"),
            ("俯身哑铃飞鸟", "images/bent_over_dumbbell_fly.png"),
            ("山羊挺身", "images/back_extension.png"),
            ("侧平举", "images/lateral_raise.png"),
            ("平板支撑", "images/plank.png"),
            ("登山跑", "images/mountain_climber.png"),
            ("负重深蹲", "images/weighted_squat.png"),
            ("拉力器划船", "images/resistance_band_row.png"),
            ("提踵", "images/calf_raise.png"),
            ("壶铃摆动", "images/kettlebell_swing.png"),
            ("波比跳", "images/burpee.png"),

        ]

        for i, (name, img_path) in enumerate(self.exercise_data):
            btn = CardButton(name, img_path)
            btn.clicked.connect(lambda checked, n=name: self.on_card_clicked(n))
            row = i // 2
            col = i % 2
            scroll_layout.addWidget(btn, row, col)

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        center_layout.addWidget(scroll_area)

        main_layout.addLayout(center_layout)

        # 底部四个按钮
        bottom_layout = QHBoxLayout()

        buttons = [
            ("动作库", "ActionLibraryPage"),
            ("计划生成", "PersonalizedWorkoutPage"),
            ("历史记录", "ViewPage"),
            ("身体数据", "BodyDataPage"),
        ]

        for label, page_name in buttons:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, p=page_name: self.controller.show_page(p))
            bottom_layout.addWidget(btn)

        main_layout.addLayout(bottom_layout)



    def on_card_clicked(self, action_name):
        """每次点击都添加动作，不去重，不切换按钮状态"""
        self.selected_actions.append(action_name)
        item = QListWidgetItem(action_name)
        self.selected_list.addItem(item)

    def save_selection(self):
        """保存当前动作清单到数据库"""
        if not self.selected_actions:
            QMessageBox.warning(self, "提示", "请先添加一些动作")
            return

        try:
            from datetime import datetime
            date_str = datetime.now().strftime("%Y%m%d")  # 例如 20240526

            exercise_data = []
            for action_name in self.selected_actions:
                exercise_data.append({
                    "item": action_name,
                    "group": 1  # 默认1组
                })

            info = TrainingInfo(
                timestamp=date_str,
                exercises=[ex['item'] for ex in exercise_data],  # 取动作名列表
                n_group=[ex['group'] for ex in exercise_data]     # 取组数列表
            )

            self.controller.database_manager.save_training_record(info)
            QMessageBox.information(self, "保存成功", "训练记录已保存到数据库")
            self.selected_actions.clear()
            self.selected_list.clear()

        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存动作清单失败:\n{e}")

    def delete_selected_action(self):
        """从列表和内部数据中删除选中的动作"""
        selected_items = self.selected_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "提示", "请先选中要删除的动作")
            return

        for item in selected_items:
            row = self.selected_list.row(item)
            self.selected_list.takeItem(row)
            # 删除 selected_actions 中对应位置的动作
            if row < len(self.selected_actions):
                del self.selected_actions[row]

    def add_to_training_list(self, exercise: dict):
        """接收一个动作字典，添加到左侧训练清单中"""
        action_name = exercise.get("name", "未知动作")
        self.selected_actions.append(action_name)
        item = QListWidgetItem(action_name)
        self.selected_list.addItem(item)
