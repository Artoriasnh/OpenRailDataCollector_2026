from PyQt5.QtCore import QThread, QObject, pyqtSignal
from PyQt5.QtWidgets import QWidget, QMessageBox

from ui.generated.login_ui import Ui_LoginWindow
from ui.account_verify import test_all_connections


class ConnectionWorker(QObject):
    finished = pyqtSignal(dict)

    def __init__(self, email, password, sql_info):
        super().__init__()
        self.email = email
        self.password = password
        self.sql_info = sql_info

    def run(self):
        result = test_all_connections(self.email, self.password, self.sql_info)
        self.finished.emit(result)


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)

        self.on_login_success = on_login_success
        self._thread = None
        self._worker = None

        self._load_defaults()

        self.ui.testConnectionButton.clicked.connect(self.test_connection)
        self.ui.loginButton.clicked.connect(self.enter_main_window)

    def _load_defaults(self):
        self.ui.dbHostEdit.setText("localhost")
        self.ui.dbPortEdit.setText("5432")
        self.ui.dbNameEdit.setText("postgres")
        self.ui.dbUserEdit.setText("postgres")
        self.ui.dbSchemaEdit.setText("public")

    def _build_sql_info(self):
        return {
            "sql_host": self.ui.dbHostEdit.text().strip() or "localhost",
            "port": self.ui.dbPortEdit.text().strip() or "5432",
            "database_name": self.ui.dbNameEdit.text().strip() or "postgres",
            "sql_username": self.ui.dbUserEdit.text().strip() or "postgres",
            "sql_password": self.ui.dbPasswordEdit.text(),
            "schema_name": self.ui.dbSchemaEdit.text().strip() or "public",
        }

    def _validate_form(self):
        email = self.ui.railEmailEdit.text().strip()
        password = self.ui.railPasswordEdit.text().strip()
        sql_info = self._build_sql_info()

        if not email:
            QMessageBox.warning(self, "Missing Input", "Please enter your Open Rail email.")
            return None

        if not password:
            QMessageBox.warning(self, "Missing Input", "Please enter your Open Rail password.")
            return None

        if not sql_info["sql_password"]:
            QMessageBox.warning(self, "Missing Input", "Please enter your PostgreSQL password.")
            return None

        try:
            int(sql_info["port"])
        except Exception:
            QMessageBox.warning(self, "Invalid Input", "Database port must be an integer.")
            return None

        return email, password, sql_info

    def _run_connection_test(self, open_main=False):
        validated = self._validate_form()
        if not validated:
            return

        email, password, sql_info = validated

        self.ui.testConnectionButton.setEnabled(False)
        self.ui.loginButton.setEnabled(False)

        self._thread = QThread()
        self._worker = ConnectionWorker(email, password, sql_info)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)

        def on_finished(result):
            self.ui.testConnectionButton.setEnabled(True)
            self.ui.loginButton.setEnabled(True)

            try:
                self._thread.quit()
                self._thread.wait()
            except Exception:
                pass

            content = f"Rail: {result['rail_msg']}\nDB: {result['db_msg']}"

            if result["success"]:
                QMessageBox.information(self, "Success", content)
                if open_main:
                    self.close()
                    self.on_login_success(email, password, sql_info)
            else:
                QMessageBox.warning(self, "Connection Failed", content)

        self._worker.finished.connect(on_finished)
        self._thread.start()

    def test_connection(self):
        self._run_connection_test(open_main=False)

    def enter_main_window(self):
        self._run_connection_test(open_main=True)