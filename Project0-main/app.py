from PyQt5.QtWidgets import QApplication, QStackedWidget, QWidget, QVBoxLayout
from data_interface import LiteDataManager
from ui import (
    ActionLibraryPage,
    BodyDataPage,
    LoginPage,
    RecordPage,
    MainPage,
    ViewPage,
    PersonalizedWorkoutPage
)


class TrainingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.stacked_widget = QStackedWidget(self)
        self.database_manager = LiteDataManager("./data/test2.db")  # 带路径示例

        self.pages = {
            "LoginPage": LoginPage(self),
            "MainPage": MainPage(self),
            "ActionLibraryPage": ActionLibraryPage(self),
            "PersonalizedWorkoutPage": PersonalizedWorkoutPage(self),
            "BodyDataPage": BodyDataPage(self),
            "ViewPage": ViewPage(self),
            "zRecordPage": RecordPage(self),
        }

        for page in self.pages.values():
            self.stacked_widget.addWidget(page)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        self.show_page("LoginPage")

    def show_page(self, name):
        page = self.pages.get(name)
        if page:
            # 触发页面显示的钩子函数（如果有）
            if hasattr(page, "on_show"):
                page.on_show()
            self.stacked_widget.setCurrentWidget(page)

    def logout(self):
        self.database_manager.logout()
        self.show_page("LoginPage")


if __name__ == "__main__":
    import sys
    import os
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("./data/app.log"),
            logging.StreamHandler()
        ]
    )

    os.makedirs("data", exist_ok=True)

    app = QApplication(sys.argv)
    window = TrainingApp()
    window.setWindowTitle("训练记录系统")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
