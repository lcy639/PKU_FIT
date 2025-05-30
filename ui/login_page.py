from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, 
    QWidget, QHBoxLayout, QTabWidget, QFormLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from .base import BasePage

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
    def get_label_font():
        font = QFont()
        font.setFamily("SimHei")
        font.setPointSize(12)
        return font
    
    @staticmethod
    def get_input_font():
        font = QFont()
        font.setFamily("SimHei")
        font.setPointSize(12)
        return font

class LoginPage(BasePage):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        # 设置整体样式
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
            QLabel {
                color: #2c3e50;
                font-family: SimHei;
            }
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                font-family: SimHei;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #2196F3;
                outline: none;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-family: SimHei;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0a69b7;
            }
            QMessageBox {
                font-family: SimHei;
            }
            QTabBar::tab {
                background-color: #e6e6e6;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 15px;
                font-family: SimHei;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #2196F3;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
        """)

        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)
        
        # 添加标题
        title_label = QLabel("PKU FIT")
        title_label.setFont(FontConfig.get_title_font())
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 30px;")
        main_layout.addWidget(title_label)
        
        # 创建选项卡控件
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("QTabWidget::pane { border: none; }")
        
        # 登录选项卡
        login_tab = QWidget()
        login_layout = QVBoxLayout(login_tab)
        
        login_form = QWidget()
        login_form_layout = QFormLayout(login_form)
        
        self.username_entry = QLineEdit()
        self.username_entry.setFont(FontConfig.get_input_font())
        login_form_layout.addRow("用户名", self.username_entry)
        
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setFont(FontConfig.get_input_font())
        login_form_layout.addRow("密码", self.password_entry)
        
        login_layout.addWidget(login_form)
        
        login_btn = QPushButton("登录")
        login_btn.setFont(FontConfig.get_button_font())
        login_btn.clicked.connect(self.login)
        login_layout.addWidget(login_btn)
        
        tab_widget.addTab(login_tab, "登录")
        
        # 注册选项卡
        register_tab = QWidget()
        register_layout = QVBoxLayout(register_tab)
        
        register_form = QWidget()
        register_form_layout = QFormLayout(register_form)
        
        self.register_username_entry = QLineEdit()  # 保持接口兼容性
        self.register_username_entry.setFont(FontConfig.get_input_font())
        register_form_layout.addRow("用户名", self.register_username_entry)
        
        self.register_password_entry = QLineEdit()  # 保持接口兼容性
        self.register_password_entry.setEchoMode(QLineEdit.Password)
        self.register_password_entry.setFont(FontConfig.get_input_font())
        register_form_layout.addRow("密码", self.register_password_entry)
        
        self.confirm_password_entry = QLineEdit()
        self.confirm_password_entry.setEchoMode(QLineEdit.Password)
        self.confirm_password_entry.setFont(FontConfig.get_input_font())
        register_form_layout.addRow("确认密码", self.confirm_password_entry)
        
        register_layout.addWidget(register_form)
        
        register_btn = QPushButton("注册")
        register_btn.setFont(FontConfig.get_button_font())
        register_btn.clicked.connect(self.register)
        register_layout.addWidget(register_btn)
        
        tab_widget.addTab(register_tab, "注册")
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        tab_widget.setGraphicsEffect(shadow)
        
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)
        
        # 设置回车键事件
        self.username_entry.returnPressed.connect(
            lambda: self.password_entry.setFocus()
        )
        self.password_entry.returnPressed.connect(
            lambda: self.login()
        )
        
        self.register_username_entry.returnPressed.connect(
            lambda: self.register_password_entry.setFocus()
        )
        self.register_password_entry.returnPressed.connect(
            lambda: self.confirm_password_entry.setFocus()
        )
        self.confirm_password_entry.returnPressed.connect(
            lambda: self.register()
        )

    def login(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()
        if not username or not password:
            QMessageBox.critical(self, "错误", "用户名和密码不能为空")
            return
        try:
            if self.controller.database_manager.login(username, password):
                QMessageBox.information(self, "成功", f"欢迎，{username}！")
                self.controller.show_page("MainPage")
        except Exception as e:
            QMessageBox.critical(self, "登录失败", str(e))

    def register(self):
        username = self.register_username_entry.text().strip()
        password = self.register_password_entry.text().strip()
        confirm_password = self.confirm_password_entry.text().strip()
        
        if not username or not password:
            QMessageBox.critical(self, "错误", "用户名和密码不能为空")
            return
            
        if password != confirm_password:
            QMessageBox.critical(self, "错误", "两次输入的密码不一致")
            return
            
        try:
            self.controller.database_manager.register(username, password)
            QMessageBox.information(self, "成功", "注册成功！请登录")
            # 自动切换到登录选项卡
            tab_index = self.layout().itemAt(1).widget().indexOf(
                self.layout().itemAt(1).widget().widget(0)
            )
            self.layout().itemAt(1).widget().setCurrentIndex(tab_index)
        except Exception as e:
            QMessageBox.critical(self, "注册失败", str(e))    