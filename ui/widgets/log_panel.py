from PyQt5.QtWidgets import QPlainTextEdit


class LogPanelWidget(QPlainTextEdit):
    def __init__(self, max_lines=8000):
        super().__init__()
        self.setReadOnly(True)
        self.max_lines = max_lines

        # QPlainTextEdit 原生支持限制 block 数量
        self.document().setMaximumBlockCount(self.max_lines)

    def append_text(self, text: str):
        self.appendPlainText(text)
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def clear_logs(self):
        self.clear()

    def set_max_lines(self, max_lines: int):
        self.max_lines = max_lines
        self.document().setMaximumBlockCount(self.max_lines)