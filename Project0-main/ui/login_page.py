from PyQt5.QtWidgets import (
    QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from .base import BasePage


class LoginPage(BasePage):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("用户名"))
        self.username_entry = QLineEdit()
        layout.addWidget(self.username_entry)

        layout.addWidget(QLabel("密码"))
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_entry)

        self.username_entry.returnPressed.connect(
            lambda: self.password_entry.setFocus()
        )
        self.password_entry.returnPressed.connect(
            lambda: self.login()
        )

        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        register_btn = QPushButton("注册")
        register_btn.clicked.connect(self.register)
        layout.addWidget(register_btn)

        self.setLayout(layout)

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
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()
        if not username or not password:
            QMessageBox.critical(self, "错误", "用户名和密码不能为空")
            return
        try:
            self.controller.database_manager.register(username, password)
            QMessageBox.information(self, "成功", "注册成功！请登录")
        except Exception as e:
            QMessageBox.critical(self, "注册失败", str(e))
