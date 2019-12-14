from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QDesktopWidget, QRadioButton, QHBoxLayout, QVBoxLayout, QLabel, QMainWindow
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QTimer, Qt, QEvent, pyqtSignal

class Danmuku(QWidget):
    COLORS = {
        'red': ("231,76,60", "255,255,255"),
        'yellow': ("241,196,15", "255,255,255"),
        'orange': ("243,156,18", "255,255,255"),
        'cyan': ("26,188,156", "255,255,255"),
        'green': ("46,204,113", "255,255,255"),
        'blue': ("52,152,219", "255,255,255"),
        'purple': ("155,89,182", "255,255,255"),
        'white': ("236,240,241", "0,0,0"),
    }

    onCloseDanmu = pyqtSignal()

    def __init__(self, word, paraphrase, y, show_paraphrase = True, color = 'white'):
        super().__init__()
        self._word = word
        self._paraphrase = paraphrase
        self._show_paraphrase = show_paraphrase
        self._color = color
        self._stop_move = False
        self._show_detail = False
        self._cleared = False

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_QuitOnClose)

        self.initUI()
        self.initPosition(y)

        self.installEventFilter(self)

    def eventFilter(self, o, e):
        if e.type() == QEvent.WindowDeactivate:
            self._show_detail = False
            self._stop_move = False
            self.setWindowOpacity(0.5)
            self._continenter.hide()
            return False

        return super().eventFilter(o, e)

    def setWordQss(self):
        bg_color, font_color = Danmuku.COLORS[self._color]
        self._word_label.setStyleSheet(f"QLabel{{background-color:rgb({bg_color}); color:rgb({font_color}); padding:5; border-radius:6px}}")

    def initUI(self):
        self.setWindowOpacity(0.5)

        word = QLabel(self._word, self)
        if self._show_paraphrase:
            word.setText(word.text() + " " + self._paraphrase.splitlines()[0])

        self._word_label = word

        head = QHBoxLayout()
        head.addWidget(word)
        head.addStretch(1)
        word.setFont(QFont("Consolas", 18))

        body = QVBoxLayout()
        body.addLayout(head)
        self.setLayout(body)

        self.setWordQss()

        continenter = QWidget(self)
        continenter.setObjectName("continenter")
        continenter.setStyleSheet("#continenter{background-color:white; padding:5; border-radius:6px}")
        continenter.hide()
        self._continenter = continenter

        body.addStretch(1)
        body.addWidget(continenter)

        detail = QVBoxLayout()
        continenter.setLayout(detail)

        paraphrase = QLabel(self._paraphrase)
        paraphrase.setFont(QFont("Consolas", 15))
        paraphrase.setWordWrap(True)
        paraphrase.setMaximumWidth(300)

        detail.addWidget(paraphrase)

        rbtns = QHBoxLayout()
        for name, (color, _) in Danmuku.COLORS.items():
            rbtn = QRadioButton(None)
            qss = f"""
            QRadioButton::indicator {{ width:13px; height:13px; background-color:rgb({color}); border: 2px solid rgb({color}); }}
            QRadioButton::indicator:checked {{ border: 2px solid black; }}
            """
            rbtn.setStyleSheet(qss)
            rbtn.setChecked(name == self._color)
            rbtn.toggled.connect(self.clickColor)
            rbtn.color = name

            rbtns.addWidget(rbtn)

        detail.addLayout(rbtns)

        btns = QHBoxLayout()

        clear = QPushButton("Clear")
        clear.clicked.connect(self.clickClear)
        btns.addWidget(clear)

        switch_paraphrase = QPushButton("Hide Paraphrase" if self._show_paraphrase else "Show Paraphrase")
        switch_paraphrase.clicked.connect(self.clickSwitch)
        btns.addWidget(switch_paraphrase)
        self._switch_paraphrase = switch_paraphrase

        detail.addLayout(btns)
        self._clear = clear

        self.show()

    def clickColor(self, e):
        if e:
            sender = self.sender()
            self._color = sender.color
            self.setWordQss()

    def clickClear(self):
        self._cleared = not self._cleared
        self._clear.setText("Redo" if self._cleared else "Clear")

    def clickSwitch(self):
        self._show_paraphrase = not self._show_paraphrase
        if self._show_paraphrase:
            self._word_label.setText(self._word + self._paraphrase.splitlines()[0])
        else:
            self._word_label.setText(self._word)

        self._switch_paraphrase.setText("Hide Paraphrase" if self._show_paraphrase else "Show Paraphrase")

    def enterEvent(self, e):
        self.setWindowOpacity(1)

    def leaveEvent(self, e):
        if not self._show_detail:
            self.setWindowOpacity(0.5)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._press_point = e.globalPos() - self.pos()
            self._press_start = e.globalPos()
            e.accept()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self.move(e.globalPos() - self._press_point)
            e.accept()

    def mouseReleaseEvent(self, e):
        if (e.globalPos() - self._press_start).manhattanLength() < 10:
            self._show_detail = not self._show_detail
            if self._show_detail:
                self._stop_move = True
                self._continenter.show()
            else:
                self._stop_move = False
                self._continenter.hide()

    def initPosition(self, y):
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(12)

        w = QDesktopWidget().availableGeometry().width()
        self.move(w, y)

    def update(self):
        if self._stop_move: return
        x = self.x() - 1
        self.move(x, self.y())
        if x < -self.width():
            self._timer.stop()
            self.close()

    def closeEvent(self, e):
        self.onCloseDanmu.emit()

