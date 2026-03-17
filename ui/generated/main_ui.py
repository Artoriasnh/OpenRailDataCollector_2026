from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1360, 860)
        MainWindow.setMinimumSize(QtCore.QSize(1240, 780))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(18, 16, 18, 16)
        self.mainLayout.setSpacing(12)

        self.headerLayout = QtWidgets.QHBoxLayout()

        self.titleLabel = QtWidgets.QLabel(self.centralwidget)
        title_font = QtGui.QFont("Segoe UI", 16)
        title_font.setBold(True)
        self.titleLabel.setFont(title_font)
        self.titleLabel.setText("Open Rail Data Collector")
        self.headerLayout.addWidget(self.titleLabel)

        self.headerLayout.addStretch()

        self.settingsButton = QtWidgets.QPushButton(self.centralwidget)
        self.settingsButton.setText("Settings")
        self.headerLayout.addWidget(self.settingsButton)

        self.refreshButton = QtWidgets.QPushButton(self.centralwidget)
        self.refreshButton.setText("Refresh")
        self.headerLayout.addWidget(self.refreshButton)

        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setObjectName("PrimaryButton")
        self.startButton.setText("Start")
        self.headerLayout.addWidget(self.startButton)

        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setObjectName("DangerButton")
        self.stopButton.setText("Stop")
        self.headerLayout.addWidget(self.stopButton)

        self.mainLayout.addLayout(self.headerLayout)

        self.contentSplitter = QtWidgets.QSplitter(self.centralwidget)
        self.contentSplitter.setOrientation(QtCore.Qt.Horizontal)

        self.leftPanel = QtWidgets.QWidget()
        self.leftLayout = QtWidgets.QVBoxLayout(self.leftPanel)
        self.leftLayout.setContentsMargins(0, 0, 0, 0)
        self.leftLayout.setSpacing(12)

        self.feedGroup = QtWidgets.QGroupBox(self.leftPanel)
        self.feedGroup.setTitle("Subscription Selection")
        self.feedGroupLayout = QtWidgets.QVBoxLayout(self.feedGroup)
        self.feedGroupLayout.setContentsMargins(16, 18, 16, 16)
        self.feedGroupLayout.setSpacing(10)

        self.feedHintLabel = QtWidgets.QLabel(self.feedGroup)
        self.feedHintLabel.setWordWrap(True)
        self.feedHintLabel.setText(
            "Choose feed categories and sub-types"
        )
        self.feedGroupLayout.addWidget(self.feedHintLabel)

        self.feedSelectorContainer = QtWidgets.QWidget(self.feedGroup)
        self.feedGroupLayout.addWidget(self.feedSelectorContainer)

        self.leftLayout.addWidget(self.feedGroup, 6)

        self.optionsGroup = QtWidgets.QGroupBox(self.leftPanel)
        self.optionsGroup.setTitle("Run Options")
        self.optionsLayout = QtWidgets.QVBoxLayout(self.optionsGroup)
        self.optionsLayout.setContentsMargins(16, 18, 16, 16)
        self.optionsLayout.setSpacing(12)

        self.saveToDbCheckBox = QtWidgets.QCheckBox(self.optionsGroup)
        self.saveToDbCheckBox.setText("Save to database")
        self.optionsLayout.addWidget(self.saveToDbCheckBox)

        self.printMessagesCheckBox = QtWidgets.QCheckBox(self.optionsGroup)
        self.printMessagesCheckBox.setText("View live messages")
        self.optionsLayout.addWidget(self.printMessagesCheckBox)

        self.durableCheckBox = QtWidgets.QCheckBox(self.optionsGroup)
        self.durableCheckBox.setText("Durable subscription")
        self.optionsLayout.addWidget(self.durableCheckBox)

        self.leftLayout.addWidget(self.optionsGroup, 1)

        self.contentSplitter.addWidget(self.leftPanel)

        self.rightPanel = QtWidgets.QWidget()
        self.rightLayout = QtWidgets.QVBoxLayout(self.rightPanel)
        self.rightLayout.setContentsMargins(0, 0, 0, 0)
        self.rightLayout.setSpacing(12)

        self.statusGroup = QtWidgets.QGroupBox(self.rightPanel)
        self.statusGroup.setTitle("Runtime Status")
        self.statusGrid = QtWidgets.QGridLayout(self.statusGroup)
        self.statusGrid.setContentsMargins(16, 18, 16, 16)
        self.statusGrid.setHorizontalSpacing(14)
        self.statusGrid.setVerticalSpacing(10)

        self.statusTextLabel = QtWidgets.QLabel("Status:")
        self.statusLabel = QtWidgets.QLabel("stopped")
        self.statusGrid.addWidget(self.statusTextLabel, 0, 0)
        self.statusGrid.addWidget(self.statusLabel, 0, 1)

        self.runningFeedsTextLabel = QtWidgets.QLabel("Running feeds:")
        self.runningFeedsLabel = QtWidgets.QLabel("none")
        self.runningFeedsLabel.setWordWrap(True)
        self.statusGrid.addWidget(self.runningFeedsTextLabel, 1, 0)
        self.statusGrid.addWidget(self.runningFeedsLabel, 1, 1)

        self.messageCountTextLabel = QtWidgets.QLabel("Total messages:")
        self.messageCountLabel = QtWidgets.QLabel("0")
        self.statusGrid.addWidget(self.messageCountTextLabel, 2, 0)
        self.statusGrid.addWidget(self.messageCountLabel, 2, 1)

        self.lastErrorTextLabel = QtWidgets.QLabel("Last error:")
        self.lastErrorLabel = QtWidgets.QLabel("")
        self.lastErrorLabel.setWordWrap(True)
        self.statusGrid.addWidget(self.lastErrorTextLabel, 3, 0)
        self.statusGrid.addWidget(self.lastErrorLabel, 3, 1)

        self.rightLayout.addWidget(self.statusGroup)

        self.tabs = QtWidgets.QTabWidget(self.rightPanel)

        self.logTab = QtWidgets.QWidget()
        self.logTabLayout = QtWidgets.QVBoxLayout(self.logTab)
        self.logTabLayout.setContentsMargins(12, 12, 12, 12)
        self.logPanelContainer = QtWidgets.QWidget(self.logTab)
        self.logTabLayout.addWidget(self.logPanelContainer)
        self.tabs.addTab(self.logTab, "Live Log")

        self.infoTab = QtWidgets.QWidget()
        self.infoTabLayout = QtWidgets.QVBoxLayout(self.infoTab)
        self.infoTabLayout.setContentsMargins(12, 12, 12, 12)
        self.infoTabLayout.setSpacing(12)

        self.dbGroup = QtWidgets.QGroupBox(self.infoTab)
        self.dbGroup.setTitle("Database Information")
        self.dbForm = QtWidgets.QFormLayout(self.dbGroup)
        self.dbForm.setContentsMargins(16, 18, 16, 16)
        self.dbForm.setHorizontalSpacing(18)
        self.dbForm.setVerticalSpacing(10)

        self.dbHostValue = QtWidgets.QLabel(self.dbGroup)
        self.dbForm.addRow("Host", self.dbHostValue)

        self.dbPortValue = QtWidgets.QLabel(self.dbGroup)
        self.dbForm.addRow("Port", self.dbPortValue)

        self.dbNameValue = QtWidgets.QLabel(self.dbGroup)
        self.dbForm.addRow("Database", self.dbNameValue)

        self.dbUserValue = QtWidgets.QLabel(self.dbGroup)
        self.dbForm.addRow("User", self.dbUserValue)

        self.dbSchemaValue = QtWidgets.QLabel(self.dbGroup)
        self.dbForm.addRow("Schema", self.dbSchemaValue)

        self.infoTabLayout.addWidget(self.dbGroup)

        self.selectionGroup = QtWidgets.QGroupBox(self.infoTab)
        self.selectionGroup.setTitle("Current Selection")
        self.selectionLayout = QtWidgets.QVBoxLayout(self.selectionGroup)
        self.selectionLayout.setContentsMargins(16, 18, 16, 16)

        self.currentSelectionLabel = QtWidgets.QLabel(self.selectionGroup)
        self.currentSelectionLabel.setWordWrap(True)
        self.currentSelectionLabel.setText("Selected subscriptions: none")
        self.selectionLayout.addWidget(self.currentSelectionLabel)

        self.infoTabLayout.addWidget(self.selectionGroup)
        self.infoTabLayout.addStretch()

        self.tabs.addTab(self.infoTab, "Configuration")
        self.rightLayout.addWidget(self.tabs)

        self.contentSplitter.addWidget(self.rightPanel)
        self.contentSplitter.setStretchFactor(0, 5)
        self.contentSplitter.setStretchFactor(1, 3)

        self.mainLayout.addWidget(self.contentSplitter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Open Rail Data Collector")