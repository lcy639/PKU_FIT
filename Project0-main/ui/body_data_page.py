import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QMessageBox, QHBoxLayout, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from .base import BasePage

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_interface import LiteDataManager, BodyStats  # noqa


height_label_string = '身高（cm）'
weight_label_string = '体重（kg）'


class BodyDataPage(BasePage):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database_manager: LiteDataManager = controller.database_manager
        self.init_ui()
        self.load_latest_data()  # 启动时加载最近保存的数据

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 日期选择器
        self.date_selector = QDateEdit(self)
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        layout.addWidget(self.date_selector, alignment=Qt.AlignCenter)

        form_layout = QFormLayout()
        self.inputs = {}

        for field in [height_label_string, weight_label_string]:
            line_edit = QLineEdit()
            self.inputs[field] = line_edit
            form_layout.addRow(QLabel(field), line_edit)
            if field in (height_label_string, weight_label_string):
                line_edit.textChanged.connect(self.calculate_bmi)

        # BMI 只读标签
        self.bmi_label = QLabel("N/A")
        form_layout.addRow(QLabel("BMI"), self.bmi_label)

        layout.addLayout(form_layout)

        # 按钮区
        button_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_data)

        calc_btn = QPushButton("计算 BMI")
        calc_btn.clicked.connect(self.calculate_bmi)

        back_btn = QPushButton("返回")
        back_btn.clicked.connect(lambda: self.controller.show_page("MainPage"))

        button_layout.addWidget(save_btn)
        button_layout.addWidget(calc_btn)
        button_layout.addWidget(back_btn)
        layout.addLayout(button_layout)

    def calculate_bmi(self):
        try:
            height_cm = float(self.inputs[height_label_string].text())
            weight_kg = float(self.inputs[weight_label_string].text())
            height_m = height_cm / 100
            bmi = weight_kg / (height_m ** 2)
            self.bmi_label.setText(f"{bmi:.2f}")
        except Exception:
            self.bmi_label.setText("N/A")

    def save_data(self):
        try:
            date_str = self.date_selector.date().toString("yyyyMMdd")
            height = float(self.inputs[height_label_string].text())
            weight = float(self.inputs[weight_label_string].text())

            body_stats = BodyStats(
                timestamp=date_str,
                height=height,
                weight=weight,
            )
            self.database_manager.save_body_stats(body_stats)
            QMessageBox.information(self, "保存成功", "身体数据已保存")
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"错误信息：{str(e)}")

    def load_latest_data(self):
        try:
            stats_list = self.database_manager.get_body_stats_history(limit=1)
            if stats_list:
                latest = stats_list[0]
                self.date_selector.setDate(
                    QDate.fromString(latest.timestamp, "yyyyMMdd")
                )
                self.inputs[height_label_string].setText(str(latest.height))
                self.inputs[weight_label_string].setText(str(latest.weight))
                self.calculate_bmi()
        except Exception as e:
            # 可以选择打印日志或忽略错误
            print(f"加载身体数据失败: {e}")
