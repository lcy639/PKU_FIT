import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PyQt5.QtWidgets import (
    QWidget, QLabel, QTextEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from backend import TrainingInfo

class ViewPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.manager = controller.manager

        layout = QVBoxLayout()

        title_label = QLabel("训练记录查看")
        layout.addWidget(title_label)

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)

        #其实下段(返回新增记录页)可以删掉，怪可惜的留着吧
        back_btn = QPushButton("返回新增记录页")
        back_btn.clicked.connect(lambda: self.controller.show_page("RecordPage"))
        layout.addWidget(back_btn)

        back_main_btn = QPushButton("返回主界面")
        back_main_btn.clicked.connect(lambda: self.controller.show_page("MainPage"))
        layout.addWidget(back_main_btn)

        self.setLayout(layout)

    def load_data(self):
        self.text_area.clear()
        try:
            data = self.manager.get_data()
            if not data:
                self.text_area.setPlainText("暂无训练记录。")
                return

            output = ""
            for date, info_dict in sorted(data.items()):
                # 格式化日期 例如：20240520 -> 2024-05-20
                if len(date) == 8 and date.isdigit():
                    date_fmt = f"{date[:4]}-{date[4:6]}-{date[6:]}"
                else:
                    date_fmt = date

                info = TrainingInfo.from_dict(info_dict)
                output += f"日期: {date_fmt}\n"
                for i, ex in enumerate(info.exercises):
                    parts = ", ".join(info.parts[i])
                    time = info.time[i]
                    output += f"  - 动作: {ex} | 部位: {parts} | 时间: {time}分钟\n"
                output += "\n"

            self.text_area.setPlainText(output)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败: {e}")
