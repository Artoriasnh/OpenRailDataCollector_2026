import logging
import re
from datetime import datetime
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QVBoxLayout, QFileDialog

from ui.generated.main_ui import Ui_MainWindow
from ui.settings_window import SettingsWindow
from ui.widgets.feed_selector import FeedSelectorWidget
from ui.widgets.log_panel import LogPanelWidget
from ui.qt_log_handler import QtLogHandler

from Message_to_sql import TD_msg, TM_MVT_msg, VSTP_msg, RTPPM_msg
from get_data import get_data
from MSG import table_format, topic_dict, Listener_dict, TM_MESSAGES


class MainWindow(QMainWindow):
    def __init__(self, email: str, password: str, sql_info: dict):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.email = email
        self.password = password
        self.sql_info = sql_info
        self.workers = []
        self.logger = None
        self.qt_log_handler = None

        self.runtime_collecting = False
        self.runtime_total_message_count = 0
        self.runtime_last_error = ""

        self._status_refresh_every = 50
        self._pending_status_updates = 0

        self.settings_data = {
            "rail_host": "publicdatafeeds.networkrail.co.uk",
            "rail_port": 61618,
            "durable": False,
        }

        self.feed_selector = FeedSelectorWidget()
        feed_container_layout = QVBoxLayout(self.ui.feedSelectorContainer)
        feed_container_layout.setContentsMargins(0, 0, 0, 0)
        feed_container_layout.addWidget(self.feed_selector)

        self.log_panel = LogPanelWidget(max_lines=3000)
        log_container_layout = QVBoxLayout(self.ui.logPanelContainer)
        log_container_layout.setContentsMargins(0, 0, 0, 0)
        log_container_layout.addWidget(self.log_panel)

        self.ui.saveToDbCheckBox.setChecked(True)
        self.ui.printMessagesCheckBox.setChecked(False)
        self.ui.durableCheckBox.setChecked(False)

        self.ui.settingsButton.clicked.connect(self.open_settings)
        self.ui.startButton.clicked.connect(self.start_collection)
        self.ui.stopButton.clicked.connect(self.stop_collection)
        self.ui.refreshButton.clicked.connect(self.handle_refresh)
        self.feed_selector.tree.itemChanged.connect(self.handle_feed_tree_changed)

        self.refresh_status()

    def _detach_old_qt_log_handler(self):
        if self.logger is not None and self.qt_log_handler is not None:
            try:
                self.logger.removeHandler(self.qt_log_handler)
            except Exception:
                pass
        self.qt_log_handler = None

    def _safe_name(self, value: str) -> str:
        text = str(value).strip().lower()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        text = re.sub(r"-+", "-", text).strip("-")
        return text or "sub"

    def _build_subscription_meta(self, feed_kind: str, detail: str):
        base = f"{feed_kind}-{detail}"
        safe = self._safe_name(base)
        return {
            "client_id": self.email.strip(),
            "subscription_name": safe,
            "subscription_id": safe,
        }

    def setup_logger(self):
        logger_name = f"MainWindowLogger_{id(self)}"
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        for h in list(self.logger.handlers):
            self.logger.removeHandler(h)

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = f"Log_{now}.txt"

        formatter = logging.Formatter("%(asctime)s - %(message)s")

        file_handler = logging.FileHandler(self.log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.qt_log_handler = QtLogHandler()
        self.qt_log_handler.setFormatter(formatter)
        self.qt_log_handler.emitter.log_signal.connect(self._append_runtime_log)
        self.logger.addHandler(self.qt_log_handler)

    def _append_runtime_log(self, text: str):
        self.log_panel.append_text(text)
        self.runtime_total_message_count += 1
        self._pending_status_updates += 1

        lowered = text.lower()
        if "error" in lowered or "failed" in lowered or "exception" in lowered:
            self.runtime_last_error = text
            self.refresh_status()
            self._pending_status_updates = 0
            return

        if self._pending_status_updates >= self._status_refresh_every:
            self.refresh_status()
            self._pending_status_updates = 0

    def append_log(self, text: str):
        self.log_panel.append_text(text)

    def open_settings(self):
        try:
            dialog = SettingsWindow(self.settings_data)
            if dialog.exec_():
                self.ui.durableCheckBox.setChecked(self.settings_data.get("durable", False))
                self.append_log(
                    f"Settings updated: host={self.settings_data.get('rail_host')} "
                    f"port={self.settings_data.get('rail_port')} "
                    f"durable={self.settings_data.get('durable')}"
                )
                self.refresh_status()
            else:
                self.append_log("Settings dialog cancelled")
        except Exception as e:
            QMessageBox.warning(self, "Settings Error", str(e))
            self.runtime_last_error = str(e)
            self.refresh_status()

    def handle_refresh(self):
        self.refresh_status()
        self.append_log("Status refreshed")

    def handle_feed_tree_changed(self, item, column):
        text = item.text(0)

        if text != "Derby":
            self.refresh_status()
            return

        checked = item.checkState(0) == Qt.Checked

        if checked:
            current_path = self.settings_data.get("derby_sop_path", "").strip()

            if current_path and Path(current_path).exists():
                self.settings_data["derby_enabled"] = True
                self.refresh_status()
                return

            file_path = self._prompt_and_select_sop_file("Derby")

            if file_path:
                self.settings_data["derby_sop_path"] = file_path
                self.settings_data["derby_enabled"] = True
                self.append_log(f"Derby SOP selected: {file_path}")
            else:
                self.feed_selector.tree.blockSignals(True)
                item.setCheckState(0, Qt.Unchecked)
                self.feed_selector.tree.blockSignals(False)

                self.settings_data["derby_enabled"] = False
                self.settings_data["derby_sop_path"] = ""
                self.append_log("Derby selection cancelled because no SOP file was provided")
        else:
            self.settings_data["derby_enabled"] = False
            self.settings_data["derby_sop_path"] = ""
            self.append_log("Derby SOP selection cleared")

        self.refresh_status()

    def _get_selection(self):
        return self.feed_selector.get_selection()

    def _update_selection_summary(self):
        feeds_list, td_list, mvt_list, rtppm_list = self._get_selection()

        parts = []
        if td_list:
            parts.append("TD: " + ", ".join(td_list))
        if mvt_list:
            parts.append("Train Movement: " + ", ".join(mvt_list))
        if "VSTP" in feeds_list:
            parts.append("VSTP")
        if rtppm_list:
            parts.append("RTPPM: " + ", ".join(rtppm_list))

        if parts:
            self.ui.currentSelectionLabel.setText("Selected subscriptions:\n" + "\n".join(parts))
        else:
            self.ui.currentSelectionLabel.setText("Selected subscriptions: none")

    def refresh_status(self):
        self._update_selection_summary()

        self.ui.statusLabel.setText("running" if self.runtime_collecting else "stopped")

        feeds_list, _, _, _ = self._get_selection()
        if self.runtime_collecting and feeds_list:
            self.ui.runningFeedsLabel.setText(", ".join(feeds_list))
        else:
            self.ui.runningFeedsLabel.setText("none")

        self.ui.messageCountLabel.setText(str(self.runtime_total_message_count))
        self.ui.lastErrorLabel.setText(self.runtime_last_error)

        self.ui.dbHostValue.setText(self.sql_info.get("sql_host", ""))
        self.ui.dbPortValue.setText(str(self.sql_info.get("port", "")))
        self.ui.dbNameValue.setText(self.sql_info.get("database_name", ""))
        self.ui.dbUserValue.setText(self.sql_info.get("sql_username", ""))
        self.ui.dbSchemaValue.setText(self.sql_info.get("schema_name", ""))

    def start_collection(self):
        feeds_list, td_list, mvt_list, rtppm_list = self._get_selection()

        if not feeds_list:
            QMessageBox.warning(self, "Warning", "Please select at least one subscription item")
            return

        save_to_db = self.ui.saveToDbCheckBox.isChecked()
        print_messages = self.ui.printMessagesCheckBox.isChecked()
        durable = self.ui.durableCheckBox.isChecked()

        if not save_to_db and not print_messages:
            QMessageBox.warning(self, "Warning", "Enable at least one option: Save to database or View live messages")
            return

        rail_host = self.settings_data.get("rail_host", "publicdatafeeds.networkrail.co.uk")
        rail_port = int(self.settings_data.get("rail_port", 61618))

        try:
            self.log_panel.clear_logs()
            self.runtime_total_message_count = 0
            self.runtime_last_error = ""
            self._pending_status_updates = 0
            self._detach_old_qt_log_handler()
            self.setup_logger()
            self.append_log("Collection starting...")

            self.workers = []

            for i in feeds_list:
                if i == 'TD':
                    for j in td_list:
                        area_id = "All" if j == "All area" else j

                        if area_id == 'All':
                            _table_format = table_format['TD_All']
                        else:
                            _table_format = table_format['TD']

                        td_mts = TD_msg(
                            schema_name=self.sql_info['schema_name'],
                            data_type='TD_' + area_id,
                            database_name=self.sql_info['database_name'],
                            sql_username=self.sql_info['sql_username'],
                            sql_password=self.sql_info['sql_password'],
                            sql_host=self.sql_info['sql_host'],
                            port=self.sql_info['port'],
                            table_format=_table_format,
                            area_id=area_id,
                            output_writer=self.logger
                        )

                        durable_meta = self._build_subscription_meta("td", area_id)

                        td_getdata = get_data(
                            mts=td_mts,
                            username=self.email,
                            password=self.password,
                            topic=topic_dict['TD'],
                            listener=Listener_dict['TD'],
                            msg_print=print_messages,
                            sts=save_to_db,
                            isdurable=durable,
                            rail_host=rail_host,
                            rail_port=rail_port,
                            client_id=durable_meta["client_id"],
                            subscription_name=durable_meta["subscription_name"],
                            subscription_id=durable_meta["subscription_id"],
                        )
                        td_getdata.start()
                        self.workers.append(td_getdata)

                if i == 'Train Movement':
                    for j in mvt_list:
                        if j[1:5] == '0004':
                            continue

                        msg_code = j[1:5]

                        mvt_mts = TM_MVT_msg(
                            schema_name=self.sql_info['schema_name'],
                            data_type=TM_MESSAGES[msg_code],
                            database_name=self.sql_info['database_name'],
                            sql_username=self.sql_info['sql_username'],
                            sql_password=self.sql_info['sql_password'],
                            sql_host=self.sql_info['sql_host'],
                            port=self.sql_info['port'],
                            table_format=table_format['MVT'][msg_code],
                            MVT_type=msg_code,
                            output_writer=self.logger
                        )

                        durable_meta = self._build_subscription_meta("mvt", msg_code)

                        mvt_getdata = get_data(
                            mts=mvt_mts,
                            username=self.email,
                            password=self.password,
                            topic=topic_dict['MVT'],
                            listener=Listener_dict['MVT'],
                            msg_print=print_messages,
                            sts=save_to_db,
                            isdurable=durable,
                            rail_host=rail_host,
                            rail_port=rail_port,
                            client_id=durable_meta["client_id"],
                            subscription_name=durable_meta["subscription_name"],
                            subscription_id=durable_meta["subscription_id"],
                        )
                        mvt_getdata.start()
                        self.workers.append(mvt_getdata)

                if i == 'VSTP':
                    vstp_mts = VSTP_msg(
                        schema_name=self.sql_info['schema_name'],
                        data_type='VSTP',
                        database_name=self.sql_info['database_name'],
                        sql_username=self.sql_info['sql_username'],
                        sql_password=self.sql_info['sql_password'],
                        sql_host=self.sql_info['sql_host'],
                        port=self.sql_info['port'],
                        table_format=table_format['VSTP'],
                        vstp_list=["schedule", "segment", "location"],
                        output_writer=self.logger
                    )

                    durable_meta = self._build_subscription_meta("vstp", "all")

                    vstp_getdata = get_data(
                        mts=vstp_mts,
                        username=self.email,
                        password=self.password,
                        topic=topic_dict['VSTP'],
                        listener=Listener_dict['VSTP'],
                        msg_print=print_messages,
                        sts=save_to_db,
                        isdurable=durable,
                        rail_host=rail_host,
                        rail_port=rail_port,
                        client_id=durable_meta["client_id"],
                        subscription_name=durable_meta["subscription_name"],
                        subscription_id=durable_meta["subscription_id"],
                    )
                    vstp_getdata.start()
                    self.workers.append(vstp_getdata)

                if i == 'RTPPM':
                    rtppm_mts = RTPPM_msg(
                        schema_name=self.sql_info['schema_name'],
                        data_type='RTPPM',
                        database_name=self.sql_info['database_name'],
                        sql_username=self.sql_info['sql_username'],
                        sql_password=self.sql_info['sql_password'],
                        sql_host=self.sql_info['sql_host'],
                        port=self.sql_info['port'],
                        table_format=table_format['RTPPM'],
                        rtppm_list=rtppm_list,
                        output_writer=self.logger
                    )

                    detail = "-".join(rtppm_list) if rtppm_list else "all"
                    durable_meta = self._build_subscription_meta("rtppm", detail)

                    rtppm_getdata = get_data(
                        mts=rtppm_mts,
                        username=self.email,
                        password=self.password,
                        topic=topic_dict['RTPPM'],
                        listener=Listener_dict['RTPPM'],
                        msg_print=print_messages,
                        sts=save_to_db,
                        isdurable=durable,
                        rail_host=rail_host,
                        rail_port=rail_port,
                        client_id=durable_meta["client_id"],
                        subscription_name=durable_meta["subscription_name"],
                        subscription_id=durable_meta["subscription_id"],
                    )
                    rtppm_getdata.start()
                    self.workers.append(rtppm_getdata)

            self.runtime_collecting = True
            self.append_log("Collection started")
            self.refresh_status()

        except Exception as e:
            self.runtime_last_error = str(e)
            QMessageBox.warning(self, "Error", str(e))
            self.append_log(f"Start failed: {e}")
            self.refresh_status()

    def stop_collection(self):
        try:
            for worker in self.workers:
                if hasattr(worker, "stop"):
                    worker.stop()
                elif hasattr(worker, "connection") and worker.connection is not None:
                    try:
                        worker.connection.disconnect()
                    except Exception:
                        pass

            self.workers = []
            self.runtime_collecting = False
            self.append_log("Collection stopped")
            self.refresh_status()

        except Exception as e:
            self.runtime_last_error = str(e)
            QMessageBox.warning(self, "Error", str(e))
            self.append_log(f"Stop failed: {e}")
            self.refresh_status()

    def _prompt_and_select_sop_file(self, region_name: str):
        reply = QMessageBox.information(
            self,
            "SOP file required",
            f"You selected a single TD region: {region_name}.\n\n"
            f"This region requires the corresponding SOP file.\n"
            f"Click OK to choose the local SOP file.",
            QMessageBox.Ok | QMessageBox.Cancel,
            QMessageBox.Ok
        )

        if reply != QMessageBox.Ok:
            return None

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select SOP file for {region_name}",
            "",
            "SOP Files (*.SOP *.txt *.csv);;All Files (*)"
        )

        if not file_path:
            return None

        return file_path

    def closeEvent(self, event):
        try:
            self.stop_collection()
        except Exception:
            pass
        self._detach_old_qt_log_handler()
        event.accept()