import re
import threading
import time
import stomp


class get_data(threading.Thread):
    def __init__(
        self,
        mts,
        username,
        password,
        topic,
        listener,
        msg_print,
        sts,
        isdurable,
        rail_host="publicdatafeeds.networkrail.co.uk",
        rail_port=61618,
        client_id=None,
        subscription_name=None,
        subscription_id=None,
    ):
        super().__init__(daemon=True)

        self.mts = mts
        self.username = username
        self.password = password
        self.topic = topic
        self.listener = listener
        self.msg_print = msg_print
        self.sts = sts
        self.isdurable = isdurable

        self.rail_host = rail_host
        self.rail_port = int(rail_port)

        self.client_id = client_id or username
        self.subscription_name = subscription_name or self._build_default_subscription_name()
        self.subscription_id = subscription_id or self.subscription_name

        self.connection = None
        self._stop_event = threading.Event()

        self.initial_retry_delay = 2
        self.max_retry_delay = 60
        self.current_retry_delay = self.initial_retry_delay

        self.heartbeat_ms = 5000

    def _log(self, message: str):
        logger = getattr(self.mts, "logger", None)
        if logger is not None:
            try:
                logger.info(message)
                return
            except Exception:
                pass
        print(message)

    def _safe_name(self, value: str) -> str:
        text = str(value).strip().lower()
        text = re.sub(r"[^a-z0-9]+", "-", text)
        text = re.sub(r"-+", "-", text).strip("-")
        return text or "subscription"

    def _build_default_subscription_name(self) -> str:
        return f"{self._safe_name(self.username)}-{self._safe_name(self.topic)}"

    def _get_host_and_port(self):
        return self.rail_host, self.rail_port

    def _create_connection(self):
        host, port = self._get_host_and_port()

        # 明确使用 STOMP 1.2，避免 ACK 头行为不一致
        conn = stomp.Connection12(
            host_and_ports=[(host, port)],
            keepalive=True,
            heartbeats=(self.heartbeat_ms, self.heartbeat_ms)
        )

        conn.set_listener(
            "",
            self.listener(
                self.mts,
                conn,
                self.msg_print,
                self.sts,
                durable=self.isdurable
            )
        )
        return conn

    def _connect_and_subscribe(self):
        host, port = self._get_host_and_port()
        conn = self._create_connection()

        self._log(f"Connecting to {host}:{port} for topic {self.topic}")

        connect_headers = {}
        if self.isdurable:
            connect_headers["client-id"] = self.client_id

        conn.connect(
            username=self.username,
            passcode=self.password,
            wait=True,
            headers=connect_headers
        )

        subscribe_headers = {}
        ack_mode = "auto"

        if self.isdurable:
            ack_mode = "client-individual"
            subscribe_headers["activemq.subscriptionName"] = self.subscription_name

        conn.subscribe(
            destination=self.topic,
            id=self.subscription_id,
            ack=ack_mode,
            headers=subscribe_headers
        )

        self.connection = conn
        self._log(
            f"Connected and subscribed to {self.topic} "
            f"(durable={self.isdurable}, subscription={self.subscription_name}, "
            f"subscription_id={self.subscription_id}, client_id={self.client_id})"
        )

        self.current_retry_delay = self.initial_retry_delay

    def _disconnect_safely(self):
        if self.connection is not None:
            try:
                if self.connection.is_connected():
                    self.connection.disconnect()
            except Exception as e:
                self._log(f"Disconnect warning for {self.topic}: {e}")
            finally:
                self.connection = None

    def stop(self):
        self._log(f"Stopping collector for {self.topic}")
        self._stop_event.set()
        self._disconnect_safely()

        try:
            self.mts.close()
        except Exception as e:
            self._log(f"Close warning for {self.topic}: {e}")

    def _sleep_with_stop(self, seconds: int):
        end_time = time.time() + seconds
        while time.time() < end_time:
            if self._stop_event.is_set():
                return
            time.sleep(0.5)

    def run(self):
        self._log(f"Collector thread started for {self.topic}")

        while not self._stop_event.is_set():
            try:
                if self.connection is None or not self.connection.is_connected():
                    self._connect_and_subscribe()

                while not self._stop_event.is_set():
                    if self.connection is None:
                        raise RuntimeError("Connection object became None")

                    if not self.connection.is_connected():
                        raise RuntimeError("STOMP connection lost")

                    time.sleep(1)

            except Exception as e:
                if self._stop_event.is_set():
                    break

                self._log(f"Connection error on {self.topic}: {e}")
                self._disconnect_safely()

                retry_seconds = self.current_retry_delay
                self._log(f"Will retry {self.topic} in {retry_seconds} seconds")

                self._sleep_with_stop(retry_seconds)

                self.current_retry_delay = min(
                    self.current_retry_delay * 2,
                    self.max_retry_delay
                )

        self._disconnect_safely()

        try:
            self.mts.close()
        except Exception as e:
            self._log(f"Final close warning for {self.topic}: {e}")

        self._log(f"Collector thread exited for {self.topic}")