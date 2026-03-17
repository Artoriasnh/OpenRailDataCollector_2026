import json
import stomp


class Listener_(stomp.ConnectionListener):
    def __init__(self, msg_to_sql, mq: stomp.Connection, durable=False):
        self._mq = mq
        self.is_durable = durable
        self.mts = msg_to_sql
        self._ack_debug_count = 0

    def _log(self, message: str):
        logger = getattr(self.mts, "logger", None)
        if logger is not None:
            try:
                logger.info(message)
                return
            except Exception:
                pass
        print(message)

    def _ack_if_needed(self, frame):
        if not self.is_durable:
            return

        try:
            # STOMP 1.2 优先使用 ack header
            ack_id = frame.headers.get("ack")
            if ack_id:
                self._mq.ack(id=ack_id)
                return

            # 兼容旧情况
            message_id = frame.headers.get("message-id")
            if message_id:
                self._mq.ack(id=message_id)
                return

            self._ack_debug_count += 1
            if self._ack_debug_count <= 5:
                self._log(f"[ACK ERROR] no usable ack id, headers={frame.headers}")

        except Exception as e:
            self._log(f"[ACK FAILED] {e}, headers={frame.headers}")

    def on_error(self, frame):
        self._log(f"[BROKER ERROR] {frame.body}")

    def on_disconnected(self):
        self._log("[BROKER] disconnected")

    def on_message(self, frame):
        pass


class TD_Listener(Listener_):
    def __init__(self, msg_to_sql, mq: stomp.Connection, msg_print, sts, durable=False):
        self.msg_print = msg_print
        self.sts = sts
        super().__init__(msg_to_sql, mq, durable=durable)

    def on_message(self, frame):
        try:
            parsed_body = json.loads(frame.body)

            if self.msg_print:
                if self.mts.area_id == 'Derby':
                    self.mts.print_td_DY(parsed_body)
                else:
                    self.mts.print_td(parsed_body)

            if self.sts:
                if self.mts.area_id == 'Derby':
                    self.mts.insert_td_DY_frame(parsed_body, self.msg_print)
                else:
                    self.mts.insert_td_frame(parsed_body, self.msg_print)

            self._ack_if_needed(frame)

        except Exception as e:
            self._log(f"[TD ERROR] {e}")
            self._log(f"[TD ERROR HEADERS] {frame.headers}")


class TM_MVT_Listener(Listener_):
    def __init__(self, msg_to_sql, mq: stomp.Connection, msg_print, sts, durable=False):
        self.msg_print = msg_print
        self.sts = sts
        super().__init__(msg_to_sql, mq, durable=durable)

    def on_message(self, frame):
        try:
            parsed_body = json.loads(frame.body)

            if self.sts:
                if self.msg_print:
                    self.mts.print_MVT_msg(parsed_body)
                self.mts.insert_MVT_frame(parsed_body, self.msg_print)
            else:
                if self.msg_print:
                    self.mts.print_MVT_msg(parsed_body)

            self._ack_if_needed(frame)

        except Exception as e:
            self._log(f"MVT listener error: {e}")
            self._log(f"[MVT ERROR HEADERS] {frame.headers}")


class VSTP_Listener(Listener_):
    def __init__(self, msg_to_sql, mq: stomp.Connection, msg_print, sts, durable=False):
        self.msg_print = msg_print
        self.sts = sts
        super().__init__(msg_to_sql, mq, durable=durable)

    def on_message(self, frame):
        try:
            parsed_body = json.loads(frame.body)

            if self.sts:
                if self.msg_print:
                    self.mts.print_VSTP_msg(parsed_body)
                self.mts.insert_VSTP_frame(parsed_body, self.msg_print)
            else:
                if self.msg_print:
                    self.mts.print_VSTP_msg(parsed_body)

            self._ack_if_needed(frame)

        except Exception as e:
            self._log(f"VSTP listener error: {e}")
            self._log(f"[VSTP ERROR HEADERS] {frame.headers}")


class RTPPM_Listener(Listener_):
    def __init__(self, msg_to_sql, mq: stomp.Connection, msg_print, sts, durable=False):
        self.msg_print = msg_print
        self.sts = sts
        super().__init__(msg_to_sql, mq, durable=durable)

    def on_message(self, frame):
        try:
            parsed_body = json.loads(frame.body)

            if self.sts:
                if self.msg_print:
                    self.mts.print_RTPPM_msg(parsed_body)
                self.mts.insert_RTPPM_frame(parsed_body, self.msg_print)
            else:
                if self.msg_print:
                    self.mts.print_RTPPM_msg(parsed_body)

            self._ack_if_needed(frame)

        except Exception as e:
            self._log(f"RTPPM listener error: {e}")
            self._log(f"[RTPPM ERROR HEADERS] {frame.headers}")