from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QListWidgetItem,
    QScrollArea, QFrame, QMenu, QAction, QSpacerItem, QSizePolicy, QGridLayout, QMessageBox,
    QLineEdit, QLayoutItem
)
from PyQt5.QtGui import QPixmap, QMovie, QFont, QColor, QPalette
from PyQt5.QtCore import Qt
import os


# 添加全局字体配置类（建议放在文件顶部）
class FontConfig:
    @staticmethod
    def get_button_font():
        font = QFont()
        font.setFamily("SimHei")
        font.setPointSize(12)
        return font
    
    @staticmethod
    def get_menu_font():
        font = QFont()
        font.setFamily("SimHei")
        font.setPointSize(12)
        return font
    

class CardButton(QPushButton):
    def __init__(self, text, icon_path=None, gif_path=None, parent=None):
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
                border-color: #66a3ff;
            }
            QPushButton:pressed {
                background-color: #d6e5ff;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.image_container = QLabel(self)
        self.image_container.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_container)

        text_label = QLabel(text, self)
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setWordWrap(True)  # 允许文本换行
        
        # 设置字体样式
        font = QFont()
        font.setFamily("SimHei")  # 使用黑体
        font.setPointSize(11)     # 字体大小
        font.setBold(True)        # 粗体
        text_label.setFont(font)
        
        # 设置文本颜色和阴影效果
        text_label.setStyleSheet("""
            color: #333;
        """)
        
        layout.addWidget(text_label)

        self.setLayout(layout)
        
        # 优先加载GIF，否则加载静态图片
        if gif_path:
            self.load_gif(gif_path)
        elif icon_path:
            self.load_image(icon_path)

    def load_image(self, icon_path):
        # 检查是否是相对路径并构建完整路径
        if not icon_path.startswith(('http://', 'https://', '/')):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(base_dir, 'images', icon_path)
        
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_container.setPixmap(pixmap)
        else:
            # 图片加载失败时显示错误信息
            self.image_container.setText("加载失败")
            print(f"警告: 无法加载图片 {icon_path}")

    def load_gif(self, gif_path):
        # 检查是否是相对路径并构建完整路径
        if not gif_path.startswith(('http://', 'https://', '/')):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            gif_path = os.path.join(base_dir, 'images', gif_path)
        
        self.movie = QMovie(gif_path)
        if self.movie.isValid():
            self.movie.setScaledSize(QtCore.QSize(64, 64))  # 保持与图片相同尺寸
            self.image_container.setMovie(self.movie)
            self.movie.start()
        else:
            self.load_image(gif_path.replace('.gif', '.jpg'))  # 尝试加载同名图片
            print(f"警告: 无法加载GIF {gif_path}，尝试加载静态图片")

class MainPage(QWidget):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.selected_actions = []  # 这里存储所有已添加动作（包括重复）
        self.all_cards = []  # 存储所有动作卡片的引用
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 顶部设置按钮
        top_layout = QHBoxLayout()
        top_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))

        settings_btn = QPushButton("设置")
        settings_btn.setFont(FontConfig.get_button_font())  # 统一按钮字体
        settings_menu = QMenu()
        # 创建登出动作时指定字体
        logout_action = QAction("登出", self)
        logout_action.setFont(FontConfig.get_menu_font())  # 统一菜单字体
        settings_menu.addAction(logout_action)
        
        settings_btn.setMenu(settings_menu)
        if self.controller:
            logout_action.triggered.connect(self.controller.logout)
        top_layout.addWidget(settings_btn)
        main_layout.addLayout(top_layout)
        if self.controller:
            logout_action.triggered.connect(self.controller.logout)
        top_layout.addWidget(settings_btn)
        main_layout.addLayout(top_layout)

        # 中部布局：左侧清单 + 中间动作列表
        center_layout = QHBoxLayout()

        # 左侧布局（包含清单和保存按钮）
        left_layout = QVBoxLayout()

        # 左侧标题
        title_label = QLabel("已选动作")
        title_label.setAlignment(Qt.AlignCenter)
        
        # 设置标题字体
        title_font = QFont()
        title_font.setFamily("SimHei")
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        title_label.setStyleSheet("margin-bottom: 10px; color: #2c3e50;")
        left_layout.addWidget(title_label)

        self.selected_list = QListWidget()
        self.selected_list.setFixedWidth(200)
        # 设置列表项样式，默认显示黑色分割线
        self.selected_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #aaa;
                border-radius: 5px;
                background-color: #f9f9f9;
                outline: none; /* 移除选中时的虚线框 */
            }
            QListWidget::item {
                padding: 8px 10px;
                text-align: center;
                font-family: SimHei;
                font-size: 12px;
                color: #1a1a1a;
                border-bottom: 1px solid #000; /* 始终显示黑色分割线 */
                margin: 0; /* 移除默认边距 */
            }
            QListWidget::item:last-child {
                border-bottom: none; /* 最后一项不显示分割线 */
            }
            QListWidget::item:selected {
                background-color: #e6f0ff;
                color: #000;
                border-color: #000; /* 选中时分割线颜色不变 */
            }
        """)
        left_layout.addWidget(self.selected_list)

        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                font-family: SimHei;
                font-size: 12px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        save_btn.clicked.connect(self.save_selection)
        buttons_layout.addWidget(save_btn)

        # 删除按钮
        delete_btn = QPushButton("删除")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                font-family: SimHei;
                font-size: 12px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected_action)
        buttons_layout.addWidget(delete_btn)
        
        left_layout.addLayout(buttons_layout)

        center_layout.addLayout(left_layout)

        # 中间：动作库区域（包含固定的标题、搜索框和可滚动的动作列表）
        action_library_layout = QVBoxLayout()
        
        # 动作库标题（固定）
        actions_title = QLabel("动作库")
        actions_title.setAlignment(Qt.AlignCenter)
        
        # 设置动作库标题字体
        actions_font = QFont()
        actions_font.setFamily("SimHei")
        actions_font.setPointSize(18)
        actions_font.setBold(True)
        actions_title.setFont(actions_font)
        
        actions_title.setStyleSheet("margin-bottom: 15px; color: #2c3e50;")
        action_library_layout.addWidget(actions_title)

        # 搜索框（固定在顶部）
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索动作...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-family: SimHei;
                font-size: 12px;
            }
        """)
        self.search_input.setFixedWidth(200)
        
        # 连接文本变化信号到搜索函数
        self.search_input.textChanged.connect(self.search_actions)
        
        search_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))
        search_layout.addWidget(self.search_input)
        search_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding))
        action_library_layout.addLayout(search_layout)

        # 可滚动的动作列表
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QGridLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(5, 5, 5, 5)

        # 保持原有动作库不变，新增GIF支持
        self.exercise_data = [
            ("有氧跑", "test.jpg", "youyangpao.gif"),
            ("俯卧撑", "pushup.jpg", "fuwocheng.gif"),
            ("负重深蹲", "weighted_squat.jpg", "fuzhongshendun.gif"),
            ("俯身哑铃飞鸟", "dumbbell_fly.jpg", "feiniao.gif"),
            ("腿部拉伸", "crunch.jpg", "lashen.gif"),
            ("哑铃肩推", "shoulder_press.jpg", "jiantui.gif"),
            ("哑铃弯举", "dumbbell_curl.jpg", "wanju.gif"),
            ("杠铃卧推", "bench_press.jpg", "wotui.gif"),
            ("臀桥", "russian_twist.jpg", "tunqiao.jpg"),
            ("坐姿腿屈伸", "leg_extension.jpg", "tuiqushen.jpg"),
            ("骑单车", "pullup.jpg", "danche.gif"),
            ("游泳", "back_extension.jpg", "youyong.jpg"),
            ("侧平举", "cepingju.jpg", "cepingju.jpg"),
            ("平板支撑", "plank.jpg", "pingban.jpg"),
            ("侧腹拉伸", "mountain_climber.jpg", "cefu.jpg"),
            ("跳绳", "deadlift.jpg", "tiaosheng.gif"),
            ("拉力器划船", "band_row.jpg", "huachuan.gif"),
            ("提踵", "calf_raise.jpg", "tizhong.jpg"),
            ("壶铃摆动", "kettlebell_swing.jpg", "huling.jpg"),
            ("仰卧起坐", "burpee.jpg", "yangqi.gif"),
        ]

        # 计算每行显示的卡片数量
        cards_per_row = 3
        for i, (name, img_path, gif_path) in enumerate(self.exercise_data):
            btn = CardButton(name, img_path, gif_path)
            btn.clicked.connect(lambda checked, n=name: self.on_card_clicked(n))
            row = i // cards_per_row
            col = i % cards_per_row
            scroll_layout.addWidget(btn, row, col)
            
            # 保存所有卡片的引用，用于搜索过滤
            self.all_cards.append((btn, name))

        # 添加空白项使布局更美观
        for i in range(cards_per_row):
            scroll_layout.setColumnStretch(i, 1)

        scroll_content.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_content)
        action_library_layout.addWidget(scroll_area)

        center_layout.addLayout(action_library_layout)

        main_layout.addLayout(center_layout)

        # 底部四个导航按钮
        bottom_layout = QHBoxLayout()

        buttons = [
            ("动作库", "ActionLibraryPage"),
            ("计划生成", "PersonalizedWorkoutPage"),
            ("历史记录", "ViewPage"),
            ("身体数据", "BodyDataPage"),
        ]

        for label, page_name in buttons:
            btn = QPushButton(label)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    font-family: SimHei;
                    font-size: 14px;
                    font-weight: bold;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                    border-color: #999;
                }
                QPushButton:pressed {
                    background-color: #d0d0d0;
                }
            """)
            if self.controller:
                btn.clicked.connect(lambda _, p=page_name: self.controller.show_page(p))
            bottom_layout.addWidget(btn)

        main_layout.addLayout(bottom_layout)


    def get_action_font(self):
        """获取统一的动作列表字体（粗体SimHei）"""
        font = QFont("SimHei", 12, QFont.Bold)
        return font

    def add_to_training_list(self, action_name):
        """外部可调用的添加动作接口"""
        item = QListWidgetItem(action_name)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFont(self.get_action_font())  # 使用统一字体
        self.selected_list.addItem(item)
        self.selected_actions.append(action_name)

    def on_card_clicked(self, action_name):
        """每次点击都添加动作，不去重，不切换按钮状态"""
        self.selected_actions.append(action_name)
        item = QListWidgetItem(action_name)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFont(self.get_action_font())  # 使用统一字体
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

            # 假设TrainingInfo类已经正确导入
            if self.controller and hasattr(self.controller, 'database_manager'):
                from data_interface.datamanager import TrainingInfo
                
                info = TrainingInfo(
                    timestamp=date_str,
                    exercises=[ex['item'] for ex in exercise_data],  # 取动作名列表
                    n_group=[ex['group'] for ex in exercise_data]     # 取组数列表
                )

                self.controller.database_manager.save_training_record(info)
                QMessageBox.information(self, "保存成功", "训练记录已保存到数据库")
            else:
                QMessageBox.information(self, "模拟保存", f"训练记录已模拟保存：\n{self.selected_actions}")
            
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

        # 从后往前删除，避免索引变化问题
        for item in reversed(selected_items):
            row = self.selected_list.row(item)
            self.selected_list.takeItem(row)
            # 删除 selected_actions 中对应位置的动作
            if row < len(self.selected_actions):
                del self.selected_actions[row]

    def search_actions(self, text):
        """搜索动作并高亮显示匹配项"""
        text = text.strip().lower()
        
        # 处理空搜索（显示所有动作）
        if not text:
            for btn, name in self.all_cards:
                btn.show()
                # 重置样式为默认
                btn.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #aaa;
                        border-radius: 8px;
                        background-color: #fefefe;
                        text-align: center;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #e6f0ff;
                        border-color: #66a3ff;
                    }
                    QPushButton:pressed {
                        background-color: #d6e5ff;
                    }
                """)
            return
        
        # 搜索并高亮匹配的动作
        found = False
        for btn, name in self.all_cards:
            if text in name.lower():
                btn.show()
                # 高亮显示匹配的动作
                btn.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #ff9800;
                        border-radius: 8px;
                        background-color: #fff8e1;
                        text-align: center;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #ffe0b2;
                        border-color: #ff9800;
                    }
                    QPushButton:pressed {
                        background-color: #ffcc80;
                    }
                """)
                found = True
            else:
                btn.hide()
        
        # 如果没有找到任何匹配项，可以显示提示
        if not found:
            print(f"未找到包含 '{text}' 的动作")

# 简单的控制器类，用于演示
class Controller:
    def __init__(self):
        self.current_page = None
        self.database_manager = None  # 实际应用中应该初始化数据库管理器
    
    def show_page(self, page_name):
        print(f"切换到页面: {page_name}")
    
    def logout(self):
        print("用户登出")

# 主函数，用于测试
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    controller = Controller()
    window = MainPage(controller)
    window.setWindowTitle("健身动作选择")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())    