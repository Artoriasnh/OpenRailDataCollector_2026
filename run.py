import json
import logging
import signal
import sys
import time
from pathlib import Path

import Message_to_sql as mts_module
from Message_to_sql import TD_msg, TM_MVT_msg, VSTP_msg, RTPPM_msg
from get_data import get_data
from MSG import table_format, topic_dict, Listener_dict, TM_MESSAGES
from SOP_con.SOP import read_SOP, get_container, get_address_update_state_container


class DualLogger:
    """
    兼容现有代码里 output_writer/logger 的用法。
    同时输出到文件和控制台。
    """
    def __init__(self, logger: logging.Logger):
        self._logger = logger

    def info(self, message):
        self._logger.info(str(message))

    def warning(self, message):
        self._logger.warning(str(message))

    def error(self, message):
        self._logger.error(str(message))

    def debug(self, message):
        self._logger.debug(str(message))


class CollectorService:
    def __init__(self, config: dict):
        self.config = config
        self.workers = []
        self.logger = None
        self.runtime_collecting = False

    def load_logger(self):
        run_cfg = self.config.get("run_options", {})
        log_file = run_cfg.get("log_file", "logs/runtime.log")
        log_level = run_cfg.get("log_level", "INFO").upper()

        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger("DockerCollector")
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        logger.propagate = False

        for h in list(logger.handlers):
            logger.removeHandler(h)

        formatter = logging.Formatter("%(asctime)s - %(message)s")

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        self.logger = DualLogger(logger)

    def validate_config(self):
        cfg = self.config

        if "open_rail" not in cfg:
            raise ValueError("Missing section: open_rail")
        if "database" not in cfg:
            raise ValueError("Missing section: database")
        if "subscriptions" not in cfg:
            raise ValueError("Missing section: subscriptions")

        rail = cfg["open_rail"]
        db = cfg["database"]
        run_opt = cfg.get("run_options", {})
        subs = cfg["subscriptions"]

        if not rail.get("email"):
            raise ValueError("open_rail.email is required")
        if not rail.get("password"):
            raise ValueError("open_rail.password is required")

        required_db = ["sql_host", "port", "database_name", "sql_username", "sql_password", "schema_name"]
        for key in required_db:
            if key not in db:
                raise ValueError(f"database.{key} is required")

        save_to_db = bool(run_opt.get("save_to_database", True))
        view_live_messages = bool(run_opt.get("view_live_messages", False))
        if not save_to_db and not view_live_messages:
            raise ValueError("At least one of save_to_database or view_live_messages must be true")

        enabled_any = False
        for feed_name in ["TD", "Train Movement", "VSTP", "RTPPM"]:
            if subs.get(feed_name, {}).get("enabled", False):
                enabled_any = True
                break

        if not enabled_any:
            raise ValueError("No subscription is enabled")

        if subs.get("TD", {}).get("enabled", False):
            areas = subs.get("TD", {}).get("areas", [])
            if not areas:
                raise ValueError("subscriptions.TD.areas cannot be empty when TD is enabled")

            if "Derby" in areas:
                derby_sop = self.config.get("sop_files", {}).get("Derby", "").strip()
                if not derby_sop:
                    raise ValueError("Derby is selected but sop_files.Derby is empty")
                if not Path(derby_sop).exists():
                    raise ValueError(f"Derby SOP file not found: {derby_sop}")

        if subs.get("Train Movement", {}).get("enabled", False):
            types_ = subs.get("Train Movement", {}).get("types", [])
            if not types_:
                raise ValueError("subscriptions.Train Movement.types cannot be empty when Train Movement is enabled")

        if subs.get("RTPPM", {}).get("enabled", False):
            pages = subs.get("RTPPM", {}).get("pages", [])
            if not pages:
                raise ValueError("subscriptions.RTPPM.pages cannot be empty when RTPPM is enabled")

    def _safe_name(self, value: str) -> str:
        import re
        text = str(value).strip().lower()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        text = re.sub(r"-+", "-", text).strip("-")
        return text or "sub"

    def _build_subscription_meta(self, email: str, feed_kind: str, detail: str):
        base = f"{feed_kind}-{detail}"
        safe = self._safe_name(base)
        return {
            "client_id": email.strip(),
            "subscription_name": safe,
            "subscription_id": safe,
        }

    def _patch_derby_sop_if_needed(self):
        subs = self.config.get("subscriptions", {})
        td_cfg = subs.get("TD", {})
        areas = td_cfg.get("areas", [])

        if "Derby" not in areas:
            return

        derby_sop = self.config.get("sop_files", {}).get("Derby", "").strip()
        if not derby_sop:
            return

        sop_dict = read_SOP(derby_sop)
        container_dict = get_container(derby_sop)
        address_update_dict = get_address_update_state_container(derby_sop)

        mts_module.DY_SOP = sop_dict
        mts_module.state_container = container_dict
        mts_module.address_update_state_container = address_update_dict

        self.logger.info(f"Loaded Derby SOP from local file: {derby_sop}")

    def start(self):
        self.validate_config()
        self.load_logger()
        self._patch_derby_sop_if_needed()

        rail = self.config["open_rail"]
        db = self.config["database"]
        run_opt = self.config.get("run_options", {})
        subs = self.config["subscriptions"]

        email = rail["email"]
        password = rail["password"]
        rail_host = rail.get("rail_host", "publicdatafeeds.networkrail.co.uk")
        rail_port = int(rail.get("rail_port", 61618))
        durable = bool(rail.get("durable", False))

        save_to_db = bool(run_opt.get("save_to_database", True))
        view_live_messages = bool(run_opt.get("view_live_messages", False))

        self.logger.info("Collection starting...")
        self.logger.info(f"Rail host={rail_host}, port={rail_port}, durable={durable}")
        self.logger.info(f"DB host={db['sql_host']}, port={db['port']}, db={db['database_name']}, schema={db['schema_name']}")

        self.workers = []

        td_cfg = subs.get("TD", {})
        if td_cfg.get("enabled", False):
            for area_label in td_cfg.get("areas", []):
                area_id = "All" if area_label == "All area" else area_label

                if area_id == "All":
                    _table_format = table_format["TD_All"]
                else:
                    _table_format = table_format["TD"]

                td_mts = TD_msg(
                    schema_name=db["schema_name"],
                    data_type="TD_" + area_id,
                    database_name=db["database_name"],
                    sql_username=db["sql_username"],
                    sql_password=db["sql_password"],
                    sql_host=db["sql_host"],
                    port=db["port"],
                    table_format=_table_format,
                    area_id=area_id,
                    output_writer=self.logger
                )

                durable_meta = self._build_subscription_meta(email, "td", area_id)

                td_worker = get_data(
                    mts=td_mts,
                    username=email,
                    password=password,
                    topic=topic_dict["TD"],
                    listener=Listener_dict["TD"],
                    msg_print=view_live_messages,
                    sts=save_to_db,
                    isdurable=durable,
                    rail_host=rail_host,
                    rail_port=rail_port,
                    client_id=durable_meta["client_id"],
                    subscription_name=durable_meta["subscription_name"],
                    subscription_id=durable_meta["subscription_id"],
                )
                td_worker.start()
                self.workers.append(td_worker)
                self.logger.info(f"Started TD worker for area={area_id}")

        mvt_cfg = subs.get("Train Movement", {})
        if mvt_cfg.get("enabled", False):
            for text in mvt_cfg.get("types", []):
                msg_code = text[1:5]

                if msg_code == "0004":
                    self.logger.info("Skipping Train Movement 0004 as GUI does")
                    continue

                mvt_mts = TM_MVT_msg(
                    schema_name=db["schema_name"],
                    data_type=TM_MESSAGES[msg_code],
                    database_name=db["database_name"],
                    sql_username=db["sql_username"],
                    sql_password=db["sql_password"],
                    sql_host=db["sql_host"],
                    port=db["port"],
                    table_format=table_format["MVT"][msg_code],
                    MVT_type=msg_code,
                    output_writer=self.logger
                )

                durable_meta = self._build_subscription_meta(email, "mvt", msg_code)

                mvt_worker = get_data(
                    mts=mvt_mts,
                    username=email,
                    password=password,
                    topic=topic_dict["MVT"],
                    listener=Listener_dict["MVT"],
                    msg_print=view_live_messages,
                    sts=save_to_db,
                    isdurable=durable,
                    rail_host=rail_host,
                    rail_port=rail_port,
                    client_id=durable_meta["client_id"],
                    subscription_name=durable_meta["subscription_name"],
                    subscription_id=durable_meta["subscription_id"],
                )
                mvt_worker.start()
                self.workers.append(mvt_worker)
                self.logger.info(f"Started Train Movement worker for type={msg_code} {TM_MESSAGES[msg_code]}")

        vstp_cfg = subs.get("VSTP", {})
        if vstp_cfg.get("enabled", False):
            vstp_mts = VSTP_msg(
                schema_name=db["schema_name"],
                data_type="VSTP",
                database_name=db["database_name"],
                sql_username=db["sql_username"],
                sql_password=db["sql_password"],
                sql_host=db["sql_host"],
                port=db["port"],
                table_format=table_format["VSTP"],
                vstp_list=["schedule", "segment", "location"],
                output_writer=self.logger
            )

            durable_meta = self._build_subscription_meta(email, "vstp", "all")

            vstp_worker = get_data(
                mts=vstp_mts,
                username=email,
                password=password,
                topic=topic_dict["VSTP"],
                listener=Listener_dict["VSTP"],
                msg_print=view_live_messages,
                sts=save_to_db,
                isdurable=durable,
                rail_host=rail_host,
                rail_port=rail_port,
                client_id=durable_meta["client_id"],
                subscription_name=durable_meta["subscription_name"],
                subscription_id=durable_meta["subscription_id"],
            )
            vstp_worker.start()
            self.workers.append(vstp_worker)
            self.logger.info("Started VSTP worker")

        rtppm_cfg = subs.get("RTPPM", {})
        if rtppm_cfg.get("enabled", False):
            rtppm_pages = rtppm_cfg.get("pages", [])

            rtppm_mts = RTPPM_msg(
                schema_name=db["schema_name"],
                data_type="RTPPM",
                database_name=db["database_name"],
                sql_username=db["sql_username"],
                sql_password=db["sql_password"],
                sql_host=db["sql_host"],
                port=db["port"],
                table_format=table_format["RTPPM"],
                rtppm_list=rtppm_pages,
                output_writer=self.logger
            )

            detail = "-".join(rtppm_pages) if rtppm_pages else "all"
            durable_meta = self._build_subscription_meta(email, "rtppm", detail)

            rtppm_worker = get_data(
                mts=rtppm_mts,
                username=email,
                password=password,
                topic=topic_dict["RTPPM"],
                listener=Listener_dict["RTPPM"],
                msg_print=view_live_messages,
                sts=save_to_db,
                isdurable=durable,
                rail_host=rail_host,
                rail_port=rail_port,
                client_id=durable_meta["client_id"],
                subscription_name=durable_meta["subscription_name"],
                subscription_id=durable_meta["subscription_id"],
            )
            rtppm_worker.start()
            self.workers.append(rtppm_worker)
            self.logger.info(f"Started RTPPM worker with pages={rtppm_pages}")

        self.runtime_collecting = True
        self.logger.info(f"Collection started. Workers={len(self.workers)}")

    def stop(self):
        if self.logger:
            self.logger.info("Stopping collection...")

        for worker in self.workers:
            try:
                if hasattr(worker, "stop"):
                    worker.stop()
            except Exception as exc:
                if self.logger:
                    self.logger.error(f"Worker stop failed: {exc}")

        self.workers = []
        self.runtime_collecting = False

        if self.logger:
            self.logger.info("Collection stopped")


SERVICE = None


def load_config(path="setting.json"):
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def handle_shutdown(signum, frame):
    global SERVICE
    print(f"Received signal {signum}, shutting down...")
    if SERVICE is not None:
        SERVICE.stop()
    sys.exit(0)


def main():
    global SERVICE

    config = load_config("setting.json")
    SERVICE = CollectorService(config)

    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    SERVICE.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handle_shutdown(signal.SIGINT, None)


if __name__ == "__main__":
    main()