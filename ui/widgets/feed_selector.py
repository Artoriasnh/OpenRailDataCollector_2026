from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem


class FeedSelectorWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Network Rail Open Data Feeds")
        self.tree.setMinimumHeight(420)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tree)

        self._build_tree()

    def _build_tree(self):
        self.tree.clear()

        td_item = QTreeWidgetItem(self.tree)
        td_item.setText(0, "TD")
        td_item.setFlags(td_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
        td_item.setCheckState(0, Qt.Unchecked)

        td_all = QTreeWidgetItem(td_item)
        td_all.setText(0, "All area")
        td_all.setFlags(td_all.flags() | Qt.ItemIsUserCheckable)
        td_all.setCheckState(0, Qt.Unchecked)

        td_derby = QTreeWidgetItem(td_item)
        td_derby.setText(0, "Derby")
        td_derby.setFlags(td_derby.flags() | Qt.ItemIsUserCheckable)
        td_derby.setCheckState(0, Qt.Unchecked)

        tm_item = QTreeWidgetItem(self.tree)
        tm_item.setText(0, "Train Movement")
        tm_item.setFlags(tm_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
        tm_item.setCheckState(0, Qt.Unchecked)

        tm_labels = [
            '"0001": "activation"',
            '"0002": "cancellation"',
            '"0003": "movement"',
            '"0004": "_unidentified"',
            '"0005": "reinstatement"',
            '"0006": "origin change"',
            '"0007": "identity change"',
            '"0008": "_location change"',
        ]
        for text in tm_labels:
            item = QTreeWidgetItem(tm_item)
            item.setText(0, text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)

        vstp_item = QTreeWidgetItem(self.tree)
        vstp_item.setText(0, "VSTP")
        vstp_item.setFlags(vstp_item.flags() | Qt.ItemIsUserCheckable)
        vstp_item.setCheckState(0, Qt.Unchecked)

        rtppm_item = QTreeWidgetItem(self.tree)
        rtppm_item.setText(0, "RTPPM")
        rtppm_item.setFlags(rtppm_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
        rtppm_item.setCheckState(0, Qt.Unchecked)

        for text in ["NationalPage_Sector", "NationalPage_Operator", "OOCPage", "OperatorPage"]:
            item = QTreeWidgetItem(rtppm_item)
            item.setText(0, text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Unchecked)

        self.tree.expandAll()

    def get_selection(self):
        feeds_list = []
        td_list = []
        mvt_list = []
        rtppm_list = []

        top_count = self.tree.topLevelItemCount()
        for i in range(top_count):
            top = self.tree.topLevelItem(i)
            top_text = top.text(0)

            if top.childCount() == 0:
                if top.checkState(0) == Qt.Checked:
                    feeds_list.append(top_text)
                continue

            for j in range(top.childCount()):
                child = top.child(j)
                if child.checkState(0) != Qt.Checked:
                    continue

                feeds_list.append(top_text)

                if top_text == "TD":
                    td_list.append(child.text(0))
                elif top_text == "Train Movement":
                    mvt_list.append(child.text(0))
                elif top_text == "RTPPM":
                    rtppm_list.append(child.text(0))

        feeds_list = list(dict.fromkeys(feeds_list))
        return feeds_list, td_list, mvt_list, rtppm_list