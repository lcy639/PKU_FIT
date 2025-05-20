from PyQt5.QtWidgets import QApplication, QStackedWidget
from ui.login_page import LoginPage
from backend import LiteDataManager
from ui.record_page import RecordPage
from ui.view_page import ViewPage
from ui.main_page import MainPage
class TrainingApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.manager = LiteDataManager("./data/test1.db")

        self.pages = {
            "LoginPage": LoginPage(self),
            "RecordPage": RecordPage(self),
            "ViewPage": ViewPage(self),
            "MainPage":MainPage(self),
        }

        for page in self.pages.values():
            self.addWidget(page)

        self.show_page("LoginPage")

    def show_page(self, name):
        self.setCurrentWidget(self.pages[name])

    def logout(self):
        self.manager.logout()
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
