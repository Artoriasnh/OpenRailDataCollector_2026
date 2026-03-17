from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName("LoginWindow")
        LoginWindow.resize(720, 968)
        LoginWindow.setMinimumSize(QtCore.QSize(680, 780))

        self.rootLayout = QtWidgets.QVBoxLayout(LoginWindow)
        self.rootLayout.setContentsMargins(28, 24, 28, 24)
        self.rootLayout.setSpacing(18)

        self.titleLabel = QtWidgets.QLabel(LoginWindow)
        title_font = QtGui.QFont("Segoe UI", 18)
        title_font.setBold(True)
        self.titleLabel.setFont(title_font)
        self.titleLabel.setText("Open Rail Data Collector")
        self.rootLayout.addWidget(self.titleLabel)

        self.subtitleLabel = QtWidgets.QLabel(LoginWindow)
        self.subtitleLabel.setWordWrap(True)
        self.subtitleLabel.setText(
            "Sign in with your Open Rail Data Feeds account and configure PostgreSQL."
        )
        self.rootLayout.addWidget(self.subtitleLabel)

        self.groupRail = QtWidgets.QGroupBox(LoginWindow)
        self.groupRail.setTitle("Open Rail Account")
        self.railForm = QtWidgets.QFormLayout(self.groupRail)
        self.railForm.setContentsMargins(18, 22, 18, 18)
        self.railForm.setHorizontalSpacing(18)
        self.railForm.setVerticalSpacing(16)

        self.railEmailEdit = QtWidgets.QLineEdit(self.groupRail)
        self.railEmailEdit.setPlaceholderText("Email")
        self.railForm.addRow("Email", self.railEmailEdit)

        self.railPasswordEdit = QtWidgets.QLineEdit(self.groupRail)
        self.railPasswordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.railPasswordEdit.setPlaceholderText("Password")
        self.railForm.addRow("Password", self.railPasswordEdit)

        self.rootLayout.addWidget(self.groupRail)

        self.groupDb = QtWidgets.QGroupBox(LoginWindow)
        self.groupDb.setTitle("PostgreSQL")
        self.dbForm = QtWidgets.QFormLayout(self.groupDb)
        self.dbForm.setContentsMargins(18, 22, 18, 18)
        self.dbForm.setHorizontalSpacing(18)
        self.dbForm.setVerticalSpacing(16)

        self.dbHostEdit = QtWidgets.QLineEdit(self.groupDb)
        self.dbHostEdit.setPlaceholderText("localhost")
        self.dbForm.addRow("Host", self.dbHostEdit)

        self.dbPortEdit = QtWidgets.QLineEdit(self.groupDb)
        self.dbPortEdit.setPlaceholderText("5432")
        self.dbForm.addRow("Port", self.dbPortEdit)

        self.dbNameEdit = QtWidgets.QLineEdit(self.groupDb)
        self.dbForm.addRow("Database", self.dbNameEdit)

        self.dbUserEdit = QtWidgets.QLineEdit(self.groupDb)
        self.dbForm.addRow("Username", self.dbUserEdit)

        self.dbPasswordEdit = QtWidgets.QLineEdit(self.groupDb)
        self.dbPasswordEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.dbForm.addRow("Password", self.dbPasswordEdit)

        self.dbSchemaEdit = QtWidgets.QLineEdit(self.groupDb)
        self.dbForm.addRow("Schema", self.dbSchemaEdit)

        self.rootLayout.addWidget(self.groupDb)

        self.buttonRow = QtWidgets.QHBoxLayout()
        self.buttonRow.addStretch()

        self.testConnectionButton = QtWidgets.QPushButton(LoginWindow)
        self.testConnectionButton.setText("Test Connection")
        self.buttonRow.addWidget(self.testConnectionButton)

        self.loginButton = QtWidgets.QPushButton(LoginWindow)
        self.loginButton.setObjectName("PrimaryButton")
        self.loginButton.setText("Log In")
        self.buttonRow.addWidget(self.loginButton)

        self.rootLayout.addLayout(self.buttonRow)

        self.signUpButton = QtWidgets.QPushButton(LoginWindow)
        self.signUpButton.setObjectName("LinkButton")
        self.signUpButton.setText("Sign up for Open Rail account")
        self.rootLayout.addWidget(self.signUpButton, alignment=QtCore.Qt.AlignRight)

        self.statusLabel = QtWidgets.QLabel(LoginWindow)
        self.statusLabel.setText("")
        self.rootLayout.addWidget(self.statusLabel)

        self.rootLayout.addStretch()

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)

    def retranslateUi(self, LoginWindow):
        LoginWindow.setWindowTitle("Open Rail Data Collector - Login")
