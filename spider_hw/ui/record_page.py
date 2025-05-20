from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from backend import TrainingInfo

class RecordPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.manager = controller.manager

        layout = QVBoxLayout()

        layout.addWidget(QLabel("日期 (格式YYYYMMDD)"))
        self.date_entry = QLineEdit()
        layout.addWidget(self.date_entry)

        layout.addWidget(QLabel("训练动作（用逗号或中文逗号分隔）"))
        self.exercises_entry = QLineEdit()
        layout.addWidget(self.exercises_entry)

        layout.addWidget(QLabel("身体部位（用分号或中文分号分组，组内用逗号或中文逗号分隔）"))
        self.parts_entry = QLineEdit()
        layout.addWidget(self.parts_entry)

        layout.addWidget(QLabel("训练时间（分钟，用逗号或中文逗号分隔）"))
        self.time_entry = QLineEdit()
        layout.addWidget(self.time_entry)

        save_btn = QPushButton("保存训练记录")
        save_btn.clicked.connect(self.save_record)
        layout.addWidget(save_btn)

        view_btn = QPushButton("查看训练记录")
        view_btn.clicked.connect(lambda: self.controller.show_page("ViewPage"))
        layout.addWidget(view_btn)

        logout_btn = QPushButton("登出")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        self.setLayout(layout)

    def save_record(self):
        date = self.date_entry.text().strip()

        # 替换中文逗号、分号
        exercises_text = self.exercises_entry.text().replace('，', ',')
        parts_text = self.parts_entry.text().replace('，', ',').replace('；', ';')
        times_text = self.time_entry.text().replace('，', ',')

        exercises = [e.strip() for e in exercises_text.split(',') if e.strip()]
        parts = [[p.strip() for p in group.split(',')] for group in parts_text.split(';') if group.strip()]
        try:
            times = [int(t.strip()) for t in times_text.split(',') if t.strip()]
        except ValueError:
            QMessageBox.critical(self, "错误", "训练时间必须是整数，用逗号分隔")
            return

        if not (date and exercises and parts and times):
            QMessageBox.critical(self, "错误", "请完整填写所有字段")
            return
        if len(exercises) != len(parts) or len(exercises) != len(times):
            QMessageBox.critical(self, "错误", "训练动作、身体部位和时间数量必须对应")
            return

        training_info = TrainingInfo(exercises, parts, times).to_dict()

        try:
            self.manager.update_data({date: training_info})
            QMessageBox.information(self, "成功", "训练记录保存成功！")

            # 清空输入框
            self.date_entry.clear()
            self.exercises_entry.clear()
            self.parts_entry.clear()
            self.time_entry.clear()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def logout(self):
        self.manager.logout()
        self.controller.show_page("LoginPage")
