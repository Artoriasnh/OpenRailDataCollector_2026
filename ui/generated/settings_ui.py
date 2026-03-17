from PyQt5 import QtCore, QtWidgets


class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName("SettingsDialog")
        SettingsDialog.resize(520, 260)
        SettingsDialog.setMinimumSize(QtCore.QSize(500, 240))

        self.verticalLayout = QtWidgets.QVBoxLayout(SettingsDialog)
        self.verticalLayout.setContentsMargins(18, 18, 18, 18)
        self.verticalLayout.setSpacing(14)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setHorizontalSpacing(18)
        self.formLayout.setVerticalSpacing(14)

        self.hostEdit = QtWidgets.QLineEdit(SettingsDialog)
        self.formLayout.addRow("Rail Host", self.hostEdit)

        self.portEdit = QtWidgets.QLineEdit(SettingsDialog)
        self.formLayout.addRow("Rail Port", self.portEdit)

        self.durableCheckBox = QtWidgets.QCheckBox("Use durable subscription", SettingsDialog)
        self.formLayout.addRow("", self.durableCheckBox)

        self.verticalLayout.addLayout(self.formLayout)

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel,
            parent=SettingsDialog
        )
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(SettingsDialog)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle("Advanced Settings")
