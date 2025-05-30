from PyQt5.QtWidgets import (
    QLabel, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QCalendarWidget, QWidget
)
from PyQt5.QtCore import QDate
from .base import BasePage
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_interface import LiteDataManager  # noqa
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image

def apply_sporty_button_style(button, 
                               bg_color="#FF6B00", 
                               hover_color="#FF8547", 
                               pressed_color="#E65A00", 
                               text_color="white", 
                               radius=12, 
                               font_size=16, 
                               padding="10px 20px"):
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: none;
            border-radius: {radius}px;
            padding: {padding};
            font-weight: bold;
            font-size: {font_size}px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}
    """)

class MuscleOverlayWidget(QWidget):
    def __init__(self, image_dir="assets", mask_dir="assets/masks"):
        super().__init__()
        self.image_dir = image_dir
        self.mask_dir = mask_dir

        self.front_label = QLabel()
        self.back_label = QLabel()

        layout = QHBoxLayout()
        layout.addWidget(self.front_label)
        layout.addWidget(self.back_label)
        self.setLayout(layout)

    def highlight_muscles(self, muscle_list):
        # 肌群正背面分类
        front_muscles = {"chest", "abs", "biceps", "shoulders", "legs_front", "calves"}
        back_muscles = {"back", "triceps", "glutes", "legs_back", "calves"}

        # 加载 base 图
        front_base = Image.open(os.path.join(self.image_dir, "base_front.png")).convert("RGBA")
        back_base = Image.open(os.path.join(self.image_dir, "base_back.png")).convert("RGBA")

        # 合成前视图 debug中...
        front_img = front_base.copy()
        for muscle in muscle_list:
            if muscle in front_muscles:
                mask_path = os.path.join(self.mask_dir, f"{muscle}_front.png")
                if os.path.exists(mask_path):
                    overlay = Image.open(mask_path).convert("RGBA")
                    front_img = Image.alpha_composite(front_img, overlay)

        # 合成背视图
        back_img = back_base.copy()
        for muscle in muscle_list:
            if muscle in back_muscles:
                mask_path = os.path.join(self.mask_dir, f"{muscle}_back.png")
                if os.path.exists(mask_path):
                    overlay = Image.open(mask_path).convert("RGBA")
                    back_img = Image.alpha_composite(back_img, overlay)

        self.front_label.setPixmap(self.pil2pixmap(front_img).scaledToHeight(500))
        self.back_label.setPixmap(self.pil2pixmap(back_img).scaledToHeight(500))

    def pil2pixmap(self, im):
        im = im.convert("RGBA")
        data = im.tobytes("raw", "RGBA")
        qimage = QImage(data, im.width, im.height, QImage.Format_RGBA8888)
        return QPixmap.fromImage(qimage)


# 用于将训练动作映射到部位
muscle_map = {
    "深蹲": ["legs", "glutes"],
    "俯卧撑": ["chest", "triceps", "shoulders"],
    "硬拉": ["back", "glutes", "hamstrings"],
    "引体向上": ["back", "biceps"],
    "卷腹": ["abs"],
    "哑铃肩推": ["shoulders", "triceps"],
    "哑铃弯举": ["biceps"],
    "杠铃卧推": ["chest", "triceps", "shoulders"],
    "俄罗斯转体": ["abs", "obliques"],
    "坐姿腿屈伸": ["quads"],
    "俯身哑铃飞鸟": ["back", "shoulders"],
    "山羊挺身": ["lower_back", "glutes"],
    "侧平举": ["shoulders"],
    "平板支撑": ["core", "abs"],
    "登山跑": ["core", "legs", "shoulders"],
    "负重深蹲": ["legs", "glutes"],
    "拉力器划船": ["back", "biceps"],
    "提踵": ["calves"],
    "壶铃摆动": ["glutes", "hamstrings", "shoulders"],
    "波比跳": ["full_body"]
}




#进度条式日历美化
'''
class TrainingCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.date_to_total = {}  # 存储日期到训练量的映射
        self.max_total = 0       # 最大训练量用于归一化

    def paintCell(self, painter, rect, date):
        """重写单元格绘制方法"""
        super().paintCell(painter, rect, date)
        
        # 将日期转换为yyyyMMdd格式
        date_str = date.toString("yyyyMMdd")
        total = self.date_to_total.get(date_str, 0)
        
        if total > 0 and self.max_total > 0:
            # 计算进度条比例
            ratio = total / self.max_total
            bar_width = int(rect.width() * ratio)

            # 绘制进度条
            painter.save()
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(100, 200, 150, 150))  # 半透明青绿色
            bar_height = 4
            bar_rect = rect.adjusted(0, rect.height()-bar_height, 0, 0)
            bar_rect.setWidth(bar_width)
            painter.drawRect(bar_rect)
            painter.restore()
'''

#填充整个日历单元块的日历美化
class TrainingCalendar(QCalendarWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.date_to_total = {}
        self.max_total = 1  # 初始值设为1避免除零错误

    def paintCell(self, painter, rect, date):
        super().paintCell(painter, rect, date)
        
        date_str = date.toString("yyyyMMdd")
        total = self.date_to_total.get(date_str, 0)
        
        if total > 0:
            # 计算颜色透明度（根据训练量比例）
            alpha = min(150, int(200 * (total / self.max_total)))  # 限制最大透明度
            color = QColor(50, 150, 50, alpha)  # 深绿色系
            
            # 填充整个单元格
            painter.save()
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRect(rect)
            painter.restore()

class ViewPage(BasePage):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.database_manager: LiteDataManager = controller.database_manager
        self.all_data = []  # 保证该属性始终存在

        layout = QVBoxLayout()

        title_label = QLabel("历史训练记录")
        layout.addWidget(title_label)

        # 修改日历控件为自定义版本
        self.calendar = TrainingCalendar()
        self.calendar.clicked.connect(self.on_date_selected)
        layout.addWidget(self.calendar)

        # 显示当天训练记录的文本区域
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # 人形图案显示
        #self.figure_widget = HumanFigureWidget()
        #layout.addWidget(self.figure_widget)

        # 肌群图像显示组件（替代火柴人）
        self.muscle_overlay = MuscleOverlayWidget()
        layout.addWidget(self.muscle_overlay)

        # 按钮区域
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新记录")
        back_main_btn = QPushButton("返回主界面")

        # 应用样式
        apply_sporty_button_style(refresh_btn, bg_color="#FF6B00", hover_color="#FF8547", pressed_color="#E65A00")
        apply_sporty_button_style(back_main_btn, bg_color="#2196F3", hover_color="#42A5F5", pressed_color="#1976D2")

        refresh_btn.clicked.connect(self.load_all_data)
        back_main_btn.clicked.connect(lambda: self.controller.show_page("MainPage"))

        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(back_main_btn)
        layout.addLayout(btn_layout)


        self.setLayout(layout)

    # 在ViewPage的load_all_data中确保max_total最小为1
    def load_all_data(self):
        try:
            self.all_data = self.database_manager.get_training_records()
        
            date_to_total = {}
            for record in self.all_data:
                day_total = sum(record.n_group)
                date_str = record.timestamp
            
                date_to_total[date_str] = date_to_total.get(date_str, 0) + day_total

            # 计算最大训练量（至少为1）
            max_total = max(date_to_total.values(), default=0)
            self.calendar.max_total = max(max_total, 1)  # 确保最小为1
            self.calendar.date_to_total = date_to_total
            self.calendar.updateCells()
        
            self.on_date_selected(self.calendar.selectedDate())
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败: {e}")
            

    def on_date_selected(self, qdate: QDate):
        self.text_area.clear()
        #self.figure_widget.highlight_parts([])  # 清空上次肌群高亮
        self.muscle_overlay.highlight_muscles([])  # 改为清空图像显示

        date_str = qdate.toString("yyyyMMdd")
        matched = [rec for rec in self.all_data if rec.timestamp == date_str]

        if not matched:
            self.text_area.setPlainText("该日暂无训练记录。")
            return

        output = ""
        trained_parts = set()

        for info in matched:
            output += f"日期: {info.timestamp[:4]}-{info.timestamp[4:6]}-{info.timestamp[6:]}\n"
            for ex, n_group in zip(info.exercises, info.n_group):
                output += f"  - 动作: {ex} | 组数: {n_group}\n"
                trained_parts.update(muscle_map.get(ex, []))
            output += "\n"

        self.text_area.setPlainText(output)
        #self.figure_widget.highlight_parts(trained_parts)
        self.muscle_overlay.highlight_muscles(trained_parts)


    def on_show(self):
        self.load_all_data()
