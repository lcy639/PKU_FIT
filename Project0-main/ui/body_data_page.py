import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QFormLayout, QMessageBox, QHBoxLayout, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from .base import BasePage

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_interface import LiteDataManager, BodyStats  # noqa

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# 设置全局中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

height_label_string = '身高（cm）'
weight_label_string = '体重（kg）'


class BodyDataPage(BasePage):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database_manager: LiteDataManager = controller.database_manager

        # 初始化图表组件
        self.figure = Figure(figsize=(8, 4))
        self.ax = self.figure.add_subplot(111)
        
        self.init_ui()
        self.load_latest_data()
        self.update_chart()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 日期选择器
        self.date_selector = QDateEdit(self)
        self.date_selector.setCalendarPopup(True)
        self.date_selector.setDate(QDate.currentDate())
        layout.addWidget(self.date_selector, alignment=Qt.AlignCenter)

        # 新增时间范围选择
        self.range_combo = QComboBox()
        self.range_combo.addItems(["最近7天", "最近30天", "全部数据"])
        self.range_combo.currentIndexChanged.connect(self.update_chart)
        layout.addWidget(QLabel("显示范围:"), alignment=Qt.AlignLeft)
        layout.addWidget(self.range_combo)

        # 图表画布
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        form_layout = QFormLayout()
        self.inputs = {}

        for field in [height_label_string, weight_label_string]:
            line_edit = QLineEdit()
            self.inputs[field] = line_edit
            form_layout.addRow(QLabel(field), line_edit)
            if field in (height_label_string, weight_label_string):
                line_edit.textChanged.connect(self.calculate_bmi)

        # BMI 标签
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

    def filter_data_by_range(self, stats_list):
        """根据选择的时间范围严格过滤数据"""
        range_text = self.range_combo.currentText()
        today = datetime.now().date()  # 使用date对象而非datetime
        
        if range_text == "最近7天":
            start_date = today - timedelta(days=6)  # 包含今天共7天
        elif range_text == "最近30天":
            start_date = today - timedelta(days=29)  # 包含今天共30天
        else:  # 全部数据
            return stats_list
        
        filtered = []
        for stat in stats_list:
            try:
                # 解析日期字符串为date对象进行比较
                stat_date = datetime.strptime(stat.timestamp, "%Y%m%d").date()
                # 严格限制在时间范围内的数据
                if start_date <= stat_date <= today:
                    filtered.append(stat)
            except ValueError as e:
                print(f"日期格式错误: {stat.timestamp}, 错误: {e}")
                continue
                
        return filtered

    def update_chart(self):
        """更新体重变化折线图"""
        self.ax.clear()
        
        try:
            stats_list = self.database_manager.get_body_stats_history()
            stats_list = self.filter_data_by_range(stats_list)
            
            if not stats_list:
                self.ax.set_title("暂无数据")
                self.canvas.draw()
                return
                
            stats_list.sort(key=lambda x: x.timestamp)
            
            dates = [datetime.strptime(s.timestamp, "%Y%m%d") for s in stats_list]
            weights = [s.weight for s in stats_list]
            
            # 绘制带样式的折线图
            self.ax.plot(dates, weights, 'b-', marker='o', markersize=5, 
                        linewidth=2, label="体重变化")
            
            # 自动调整日期格式
            if dates:
                days = (dates[-1] - dates[0]).days
                if days <= 7:
                    date_fmt = mdates.DateFormatter('%m-%d')
                    locator = mdates.DayLocator()
                elif days <= 30:
                    date_fmt = mdates.DateFormatter('%m-%d')
                    locator = mdates.WeekdayLocator()
                else:
                    date_fmt = mdates.DateFormatter('%Y-%m')
                    locator = mdates.MonthLocator()
                
                self.ax.xaxis.set_major_locator(locator)
                self.ax.xaxis.set_major_formatter(date_fmt)
            
            # 设置标签样式
            self.ax.set_xlabel("日期", fontsize=10)
            self.ax.set_ylabel("体重 (kg)", fontsize=10)
            self.ax.set_title("体重变化趋势", fontsize=12)
            
            # 添加网格和调整布局
            self.ax.grid(True, linestyle='--', alpha=0.6)
            self.figure.tight_layout()
            self.figure.autofmt_xdate(rotation=45)
            self.ax.legend()
            
            self.canvas.draw()
            
        except Exception as e:
            print(f"图表更新失败: {e}")
            self.ax.set_title("数据加载失败")
            self.canvas.draw()

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
            self.update_chart()

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
            print(f"加载身体数据失败: {e}")

    def on_show(self):
        """每次页面显示时自动刷新数据"""
        self.load_latest_data()
        self.update_chart()