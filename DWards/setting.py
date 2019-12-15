from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt
import utils

class Setting(QDialog):
    onClose = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()

    def initUI(self):
        self.setWindowTitle("DWords - Setting")
        self.setWindowIcon(QIcon("img/logo.svg"))
        self.setMinimumWidth(380)

        body = QVBoxLayout()
        self.setLayout(body)

        setting = QTabWidget()
        body.addWidget(setting)

        self._global_setting = QWidget()
        self._danmuku_setting = QWidget()

        self.initGlobalSetting()
        self.initDanmukuSetting()

        setting.addTab(self._global_setting, "Global Setting")
        setting.addTab(self._danmuku_setting, "Danmuku Setting")

        btns = QHBoxLayout()
        ok = QPushButton("OK")
        apply = QPushButton("Apply")
        cancel = QPushButton("Cancel")
        btns.addStretch(1)
        btns.addWidget(ok)
        btns.addWidget(apply)
        btns.addWidget(cancel)

        body.addLayout(btns)

    def initGlobalSetting(self):
        widget = self._global_setting
        layout = QVBoxLayout()
        widget.setLayout(layout)

        label_email = QLabel("Email: ")
        edit_email = QLineEdit()

        label_password = QLabel("Password: ")
        edit_password = QLineEdit()
        edit_password.setEchoMode(QLineEdit.Password)

        label_smtp = QLabel("SMTP server: ")
        edit_smtp = QLineEdit()

        label_pop3 = QLabel("POP3 server: ")
        edit_pop3 = QLineEdit()

        layout.addWidget(label_email)
        layout.addWidget(edit_email)
        layout.addWidget(label_password)
        layout.addWidget(edit_password)
        layout.addWidget(label_smtp)
        layout.addWidget(edit_smtp)
        layout.addWidget(label_pop3)
        layout.addWidget(edit_pop3)

    def initDanmukuSetting(self):
        widget = self._danmuku_setting
        layout = QVBoxLayout()
        widget.setLayout(layout)

        label_speed = QLabel(f"Speed: {1}")
        layout.addWidget(label_speed)
        slider_speed = QSlider(Qt.Horizontal)
        slider_speed.valueChanged
        layout.addWidget(slider_speed)

        label_frequency = QLabel(f"Frequency: per {1}s")
        layout.addWidget(label_frequency)
        slider_frequency = QSlider(Qt.Horizontal)
        slider_frequency.valueChanged
        layout.addWidget(slider_frequency)

        label_color = QLabel("Default Color")
        layout.addWidget(label_color)
        colors = QHBoxLayout()
        for name, (color, _) in utils.COLORS.items():
            rbtn = QRadioButton(None)
            qss = f"""
            QRadioButton::indicator {{ width:13px; height:13px; background-color:rgb({color}); border: 2px solid rgb({color}); }}
            QRadioButton::indicator:checked {{ border: 2px solid black; }}
            """
            rbtn.setStyleSheet(qss)
            rbtn.setChecked(name == 'white')
            # rbtn.toggled.connect(self.clickColor)
            rbtn.color = name

            colors.addWidget(rbtn)
        
        layout.addLayout(colors)

        label_transparency = QLabel(f"Transparency: {1}")
        layout.addWidget(label_transparency)
        slider_transparency = QSlider(Qt.Horizontal)
        slider_transparency.valueChanged
        layout.addWidget(slider_transparency)


    def closeEvent(self, e):
        self.onClose.emit()
