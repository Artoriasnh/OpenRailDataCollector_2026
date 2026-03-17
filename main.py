import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from ui.login_window import LoginWindow
from ui.main_window import MainWindow


def load_qss(app: QApplication):
    qss_path = Path(__file__).parent / "ui" / "style.qss"
    if qss_path.exists():
        with open(qss_path,  "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    load_qss(app)

    windows = {}

    def open_main(email: str, password: str, sql_info: dict):
        windows["main"] = MainWindow(
            email=email,
            password=password,
            sql_info=sql_info,
        )
        windows["main"].show()

    windows["login"] = LoginWindow(on_login_success=open_main)
    windows["login"].show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()