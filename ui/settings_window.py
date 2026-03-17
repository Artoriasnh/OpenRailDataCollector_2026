from PyQt5.QtWidgets import QDialog, QMessageBox

from ui.generated.settings_ui import Ui_SettingsDialog


class SettingsWindow(QDialog):
    def __init__(self, settings: dict):
        super().__init__()
        self.ui = Ui_SettingsDialog()
        self.ui.setupUi(self)

        self.settings = settings or {}
        self._load_settings()

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def _load_settings(self):
        self.ui.hostEdit.setText(
            self.settings.get("rail_host", "publicdatafeeds.networkrail.co.uk")
        )
        self.ui.portEdit.setText(
            str(self.settings.get("rail_port", 61618))
        )
        self.ui.durableCheckBox.setChecked(
            self.settings.get("durable", False)
        )

    def accept(self):
        host = self.ui.hostEdit.text().strip()
        port_text = self.ui.portEdit.text().strip()

        if not host:
            QMessageBox.warning(self, "Invalid Input", "Rail Host cannot be empty.")
            return

        try:
            port = int(port_text)
        except Exception:
            QMessageBox.warning(self, "Invalid Input", "Rail Port must be an integer.")
            return

        self.settings["rail_host"] = host
        self.settings["rail_port"] = port
        self.settings["durable"] = self.ui.durableCheckBox.isChecked()

        super().accept()