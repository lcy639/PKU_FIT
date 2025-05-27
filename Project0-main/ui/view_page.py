from PyQt5.QtWidgets import (
    QLabel, QTextEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from .base import BasePage
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_interface import LiteDataManager # noqa


class ViewPage(BasePage):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database_manager: LiteDataManager = controller.database_manager

        layout = QVBoxLayout()

        title_label = QLabel("训练记录查看")
        layout.addWidget(title_label)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)

        back_main_btn = QPushButton("返回主界面")
        back_main_btn.clicked.connect(lambda: self.controller.show_page("MainPage"))
        layout.addWidget(back_main_btn)

        self.setLayout(layout)

    def load_data(self):
        self.text_area.clear()
        try:
            data = self.database_manager.get_training_records()
            if not len(data):
                self.text_area.setPlainText("暂无训练记录。")
                return

            output = ""
            for info in data:
                # 格式化日期 例如：20240520 -> 2024-05-20
                if len(info.timestamp) == 8 and info.timestamp.isdigit():
                    date_fmt = f"{info.timestamp[:4]}-{info.timestamp[4:6]}-{info.timestamp[6:]}"
                else:
                    date_fmt = info.timestamp

                output += f"日期: {date_fmt}\n"
                for ex, n_group in zip(info.exercises, info.n_group):
                    output += f"  - 动作: {ex} | 组数: {n_group}\n"
                output += "\n"

            self.text_area.setPlainText(output)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败: {e}")

    def on_show(self):
        self.load_data()
