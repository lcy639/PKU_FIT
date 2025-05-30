from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QScrollArea, QFrame, QMenu, QAction, QSpacerItem, QSizePolicy, QGridLayout, QMessageBox,
    QLineEdit, QLayoutItem, QDialog, QDialogButtonBox, QTextEdit, QApplication
)
from PyQt5.QtGui import QFont, QColor
import os
import json

# 统一字体设置
class FontConfig:
    @staticmethod
    def get_title_font():
        font = QFont()
        font.setFamily("SimHei")
        font.setPointSize(18)
        font.setBold(True)
        return font
    
    @staticmethod
    def get_subtitle_font():
        font = QFont()
        font.setFamily("SimHei")
        font.setPointSize(16)
        font.setBold(True)
        return font
    
    @staticmethod
    def get_button_font():
        font = QFont()
        font.setFamily("SimHei")
        font.setPointSize(12)
        return font
    
    @staticmethod
    def get_list_font():
        font = QFont()
        font.setFamily("SimHei")
        font.setPointSize(12)
        return font
    
    @staticmethod
    def get_card_title_font():
        font = QFont()
        font.setFamily("SimHei")
        font.setPointSize(11)
        font.setBold(True)
        return font

# 优化后的肌肉群颜色映射 - 提高对比度和识别度
class MuscleColorMap:
    COLORS = {
        "胸肌": "#FF6666",       # 更鲜艳的红色
        "背肌": "#66A3FF",       # 更鲜艳的蓝色
        "肩部": "#FFA366",       # 更鲜艳的橙色
        "二头肌": "#B366FF",     # 更鲜艳的紫色
        "三头肌": "#66FF66",     # 更鲜艳的绿色
        "腹肌": "#FF66B3",       # 更鲜艳的粉色
        "大腿": "#B3FF66",       # 更鲜艳的黄绿色
        "小腿": "#66FFB3",       # 更鲜艳的蓝绿色
        "臀部": "#FF9999",       # 调整后的玫瑰红
        "前臂": "#9999FF",       # 调整后的靛蓝色
        "斜方肌": "#FF99FF",     # 调整后的紫罗兰色
        "腰部": "#99FFFF",       # 调整后的青色
    }
    
    @staticmethod
    def get_color(muscle_name):
        """获取特定肌肉的颜色，如果不存在则返回灰色"""
        return MuscleColorMap.COLORS.get(muscle_name, "#CCCCCC")
    
    @staticmethod
    def get_all_muscles():
        """返回所有定义的肌肉名称"""
        return list(MuscleColorMap.COLORS.keys())
    
    @staticmethod
    def get_color_legend():
        """获取肌肉-颜色对照表"""
        legend = []
        for muscle, color in MuscleColorMap.COLORS.items():
            legend.append(f"{muscle}: {color}")
        return legend

class ColoredCardButton(QPushButton):
    def __init__(self, action_data, parent=None):
        super().__init__(parent)
        self.action_data = action_data
        self.setFixedSize(180, 80)
        
        # 确保有肌肉数据
        self.target_muscles = action_data.get("target_muscles", [])
        if not self.target_muscles:
            self.target_muscles = ["未知"]
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建彩色条背景
        self.color_bar = QWidget(self)
        self.color_bar.setFixedHeight(10)
        color_bar_layout = QHBoxLayout(self.color_bar)
        color_bar_layout.setContentsMargins(0, 0, 0, 0)
        color_bar_layout.setSpacing(0)
        
        # 为每个肌肉创建一个彩色条
        n = len(self.target_muscles)
        for muscle in self.target_muscles:
            color_widget = QWidget()
            color = MuscleColorMap.get_color(muscle)
            color_widget.setStyleSheet(f"background-color: {color};")
            color_bar_layout.addWidget(color_widget, 1)
        
        main_layout.addWidget(self.color_bar)
        
        # 创建卡片内容区域
        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        content_layout.setSpacing(5)
        
        # 动作名称
        name_label = QLabel(action_data.get("name", "未知动作"), self)
        name_label.setAlignment(QtCore.Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setFont(FontConfig.get_card_title_font())
        name_label.setStyleSheet("color: #333;")
        content_layout.addWidget(name_label)
        
        # 难度标签
        difficulty = action_data.get("difficulty", "未知")
        diff_label = QLabel(f"难度: {difficulty}", self)
        diff_label.setAlignment(QtCore.Qt.AlignCenter)
        diff_label.setFont(FontConfig.get_button_font())
        diff_label.setStyleSheet("color: #666; font-size: 9pt;")
        content_layout.addWidget(diff_label)
        
        main_layout.addWidget(content_widget, 1)
        
        # 设置卡片整体样式
        self.setStyleSheet("""
            QPushButton {
                border: 1px solid #aaa;
                border-radius: 8px;
                background-color: #fefefe;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #e6f0ff;
                border-color: #66a3ff;
            }
            QPushButton:pressed {
                background-color: #d6e5ff;
            }
        """)

class ActionDetailDialog(QDialog):
    def __init__(self, action_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle(action_data.get("name", "动作详情"))
        self.setMinimumSize(400, 300)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f9f9f9;
            }
            QLabel {
                font-family: SimHei;
                color: #333;
            }
            QTextEdit {
                font-family: SimHei;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        name_label = QLabel(f"<b>动作名称：</b>{action_data.get('name', '')}")
        name_label.setFont(FontConfig.get_button_font())
        layout.addWidget(name_label)

        # 肌肉群标签，带有颜色标识
        muscles = action_data.get("target_muscles", [])
        if not muscles:
            muscles_text = "目标肌肉：无数据"
        else:
            muscles_text = "<b>目标肌肉：</b>"
            for muscle in muscles:
                color = MuscleColorMap.get_color(muscle)
                muscles_text += f'<span style="color:{color}; font-weight:bold;">{muscle}</span> '
        
        muscles_label = QLabel(muscles_text)
        muscles_label.setFont(FontConfig.get_button_font())
        layout.addWidget(muscles_label)

        equipment_label = QLabel(f"<b>器械：</b>{action_data.get('equipment', '无')}")
        equipment_label.setFont(FontConfig.get_button_font())
        layout.addWidget(equipment_label)

        difficulty_label = QLabel(f"<b>难度：</b>{action_data.get('difficulty', '未知')}")
        difficulty_label.setFont(FontConfig.get_button_font())
        layout.addWidget(difficulty_label)

        description_label = QLabel("<b>动作描述：</b>")
        description_label.setFont(FontConfig.get_button_font())
        layout.addWidget(description_label)

        description_text = QTextEdit()
        description_text.setReadOnly(True)
        description_text.setText(action_data.get("description", ""))
        description_text.setFont(FontConfig.get_button_font())
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
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        top_layout = QHBoxLayout()
        top_layout.addStretch()

        # 添加标题
        title_label = QLabel("动作库")
        title_label.setFont(FontConfig.get_title_font())
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(title_label)

        # 添加设置按钮
        settings_btn = QPushButton("设置")
        settings_btn.setFont(FontConfig.get_button_font())
        settings_menu = QMenu()
        logout_action = QAction("登出", self)
        settings_menu.addAction(logout_action)
        settings_btn.setMenu(settings_menu)
        logout_action.triggered.connect(self.controller.logout)
        top_layout.addWidget(settings_btn)
        main_layout.addLayout(top_layout)

        # 添加肌肉颜色对照表
        legend_label = QLabel("肌肉颜色对照表:")
        legend_label.setFont(FontConfig.get_button_font())
        main_layout.addWidget(legend_label)
        
        legend_text = ""
        for i, (muscle, color) in enumerate(MuscleColorMap.COLORS.items()):
            legend_text += f'<span style="color:{color}; font-weight:bold;">{muscle}</span> '
            if (i + 1) % 4 == 0:
                legend_text += "<br>"
        
        legend_content = QLabel(legend_text)
        legend_content.setFont(FontConfig.get_button_font())
        main_layout.addWidget(legend_content)

        # 添加动作内容
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f9f9f9;
            }
        """)
        main_layout.addWidget(self.scroll_area)

        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(10)

        self.scroll_area.setWidget(self.scroll_content)

        # 返回主页面按钮
        back_btn = QPushButton("返回主页面")
        back_btn.setFont(FontConfig.get_button_font())
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a69b7;
            }
        """)
        back_btn.clicked.connect(lambda: self.controller.show_page("MainPage"))
        main_layout.addWidget(back_btn)

    def load_actions(self):
        # 使用完整的动作数据
        self.actions = [
            {
                "name": "有氧跑",
                "target_muscles": ["大腿", "小腿", "臀部"],
                "equipment": "跑步机/户外",
                "difficulty": "低",
                "description": "保持稳定的跑步节奏，提高心肺功能和下肢耐力。"
            },
            {
                "name": "俯卧撑",
                "target_muscles": ["胸肌", "三头肌", "肩部"],
                "equipment": "无",
                "difficulty": "中",
                "description": "双手撑地，与肩同宽，身体保持一条直线，下降并撑起身体。"
            },
            {
                "name": "负重深蹲",
                "target_muscles": ["大腿", "臀部", "腰部"],
                "equipment": "杠铃",
                "difficulty": "高",
                "description": "肩负杠铃，双脚与肩同宽，下蹲至大腿与地面平行，然后站起。"
            },
            {
                "name": "俯身哑铃飞鸟",
                "target_muscles": ["背肌", "肩部"],
                "equipment": "哑铃",
                "difficulty": "中",
                "description": "俯身约90度，双手持哑铃向两侧展开，感受背部收缩。"
            },
            {
                "name": "腿部拉伸",
                "target_muscles": ["大腿", "小腿", "臀部"],
                "equipment": "无",
                "difficulty": "低",
                "description": "站立或坐姿，对大腿前侧、后侧和小腿进行静态拉伸。"
            },
            {
                "name": "哑铃肩推",
                "target_muscles": ["肩部", "三头肌"],
                "equipment": "哑铃",
                "difficulty": "中",
                "description": "坐姿，双手持哑铃从肩部向上推起至手臂伸直。"
            },
            {
                "name": "哑铃弯举",
                "target_muscles": ["二头肌"],
                "equipment": "哑铃",
                "difficulty": "低",
                "description": "站立或坐姿，双手持哑铃，上臂固定，弯曲肘部将哑铃举起。"
            },
            {
                "name": "杠铃卧推",
                "target_muscles": ["胸肌", "三头肌", "肩部"],
                "equipment": "杠铃",
                "difficulty": "高",
                "description": "平躺在卧推凳上，双手握住杠铃，向上推起至手臂伸直。"
            },
            {
                "name": "臀桥",
                "target_muscles": ["臀部", "大腿"],
                "equipment": "无",
                "difficulty": "低",
                "description": "仰卧，屈膝，双脚踩地，臀部抬起至身体呈一条直线。"
            },
            {
                "name": "坐姿腿屈伸",
                "target_muscles": ["大腿"],
                "equipment": "腿屈伸机",
                "difficulty": "中",
                "description": "坐在腿屈伸机上，双脚勾住踏板，伸直膝关节。"
            },
            {
                "name": "骑单车",
                "target_muscles": ["大腿", "臀部", "小腿"],
                "equipment": "动感单车",
                "difficulty": "中",
                "description": "模拟骑自行车的动作，可调节阻力进行有氧训练。"
            },
            {
                "name": "游泳",
                "target_muscles": ["背肌", "肩部", "胸肌", "手臂", "大腿"],
                "equipment": "游泳池",
                "difficulty": "中",
                "description": "全身性运动，锻炼心肺功能和肌肉耐力。"
            },
            {
                "name": "侧平举",
                "target_muscles": ["肩部"],
                "equipment": "哑铃",
                "difficulty": "低",
                "description": "站立，双手持哑铃向两侧平举至肩部高度。"
            },
            {
                "name": "平板支撑",
                "target_muscles": ["腹肌", "肩部", "手臂", "背部"],
                "equipment": "无",
                "difficulty": "中",
                "description": "双肘和双脚支撑地面，保持身体呈一条直线，核心收紧。"
            },
            {
                "name": "侧腹拉伸",
                "target_muscles": ["腹肌", "腰部"],
                "equipment": "无",
                "difficulty": "低",
                "description": "站立，向一侧弯曲身体，感受侧腹部的拉伸。"
            },
            {
                "name": "跳绳",
                "target_muscles": ["小腿", "肩部", "手臂"],
                "equipment": "跳绳",
                "difficulty": "中",
                "description": "双脚跳跃，同时挥动跳绳，可调节速度和节奏。"
            },
            {
                "name": "拉力器划船",
                "target_muscles": ["背肌", "二头肌"],
                "equipment": "拉力器",
                "difficulty": "中",
                "description": "双脚踩住拉力器，身体后倾，将把手拉向腹部。"
            },
            {
                "name": "提踵",
                "target_muscles": ["小腿"],
                "equipment": "无",
                "difficulty": "低",
                "description": "站立，脚跟抬起，脚尖着地，然后缓慢放下。"
            },
            {
                "name": "壶铃摆动",
                "target_muscles": ["臀部", "大腿", "背部"],
                "equipment": "壶铃",
                "difficulty": "中",
                "description": "双脚与肩同宽，双手握住壶铃，前后摆动。"
            },
            {
                "name": "仰卧起坐",
                "target_muscles": ["腹肌"],
                "equipment": "无",
                "difficulty": "低",
                "description": "仰卧，屈膝，双手抱头，上半身抬起。"
            }
        ]

        self.populate_actions()

    def populate_actions(self):
        # 清空旧的内容
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for i, action in enumerate(self.actions):
            btn = ColoredCardButton(action, self)
            btn.clicked.connect(lambda checked, a=action: self.show_detail(a))

            row = i // 3  # 每行显示3个卡片
            col = i % 3
            self.scroll_layout.addWidget(btn, row, col)

    def show_detail(self, action_data):
        dialog = ActionDetailDialog(action_data, self)
        dialog.exec_()

# 简单的控制器类，用于演示
class Controller:
    def __init__(self):
        self.current_page = None
    
    def show_page(self, page_name):
        print(f"切换到页面: {page_name}")
    
    def logout(self):
        print("用户登出")

# 主函数，用于测试
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    controller = Controller()
    window = ActionLibraryPage(controller)
    window.setWindowTitle("健身动作库")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())    