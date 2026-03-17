import logging
from PyQt5.QtCore import QObject, pyqtSignal


class LogEmitter(QObject):
    log_signal = pyqtSignal(str)


class QtLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.emitter = LogEmitter()

    def emit(self, record):
        try:
            msg = self.format(record)
            self.emitter.log_signal.emit(msg)
        except Exception:
            self.handleError(record)