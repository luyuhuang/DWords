from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QMouseEvent
from PyQt5.QtCore import QTimer, Qt, QEvent, pyqtSignal, QRect
from . import utils

class WordLabel(QLabel):
    onEnter = pyqtSignal()
    onLeave = pyqtSignal()
    onMousePress = pyqtSignal(QMouseEvent)
    onMouseMove = pyqtSignal(QMouseEvent)
    onMouseRelease = pyqtSignal(QMouseEvent)

    def __init__(self, *argv, **kw):
        super().__init__(*argv, **kw)

        self.installEventFilter(self)

    def enterEvent(self, e):
        self.onEnter.emit()

    def leaveEvent(self, e):
        self.onLeave.emit()

    def mousePressEvent(self, e):
        self.onMousePress.emit(e)

    def mouseMoveEvent(self, e):
        self.onMouseMove.emit(e)

    def mouseReleaseEvent(self, e):
        self.onMouseRelease.emit(e)

class Danmaku(QWidget):
    onModified = pyqtSignal(str)

    def __init__(self, word, paraphrase, y, show_paraphrase = None, color = None):
        super().__init__()
        self._word = word
        self._paraphrase = paraphrase
        self._stop_move = False
        self._show_detail = False

        self.modified = False
        self._show_paraphrase = show_paraphrase \
            if show_paraphrase is not None else \
            utils.get_setting("danmaku_default_show_paraphrase")
        self._color = color if color is not None else \
            utils.get_setting("danmaku_default_color")
        self._cleared = False

        self.setWindowFlags(
            self.windowFlags() |
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.ToolTip |
            Qt.X11BypassWindowManagerHint  # for gnome
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.initUI()
        self.initPosition(y)

        # self.installEventFilter(self)

    # def eventFilter(self, o, e):
    #     # due to flag `X11BypassWindowManagerHint`, event `WindowDeactivate` doesn't work
    #     if e.type() == QEvent.WindowDeactivate:
    #         self._show_detail = False
    #         self._stop_move = False
    #         self.setWindowOpacity(0.5)
    #         self._continenter.hide()
    #         return False

    #     return super().eventFilter(o, e)

    @property
    def show_paraphrase(self):
        return self._show_paraphrase

    @show_paraphrase.setter
    def show_paraphrase(self, value):
        self._show_paraphrase = value
        self.modified = True
        self.onModified.emit('show_paraphrase')

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self.modified = True
        self.onModified.emit('color')

    @property
    def cleared(self):
        return self._cleared

    @cleared.setter
    def cleared(self, value):
        self._cleared = value
        self.modified = True
        self.onModified.emit('cleared')

    def setWordQss(self):
        bg_color, font_color = utils.COLORS[self.color]
        self._word_label.setStyleSheet(f"QLabel{{background-color:rgb({bg_color}); color:rgb({font_color}); padding:5; border-radius:6px}}")

    def initUI(self):
        self.setWindowOpacity(utils.get_setting("danmaku_transparency"))

        word = WordLabel(self._word)
        if self.show_paraphrase:
            word.setText(word.text() + " " + self._paraphrase.splitlines()[0])

        word.onEnter.connect(self.enterWordEvent)
        word.onLeave.connect(self.leaveWordEvent)
        word.onMousePress.connect(self.mousePressWordEvent)
        word.onMouseMove.connect(self.mouseMoveWordEvent)
        word.onMouseRelease.connect(self.mouseReleaseWordEvent)

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
        paraphrase.setStyleSheet("QLabel{color:black;}")
        paraphrase.setWordWrap(True)
        paraphrase.setMaximumWidth(300)

        detail.addWidget(paraphrase)

        rbtns = QHBoxLayout()
        for name, (color, _) in utils.COLORS.items():
            rbtn = QRadioButton(None)
            qss = f"""
            QRadioButton::indicator {{ width:13px; height:13px; background-color:rgb({color}); border: 2px solid rgb({color}); }}
            QRadioButton::indicator:checked {{ border: 2px solid black; }}
            """
            rbtn.setStyleSheet(qss)
            rbtn.setChecked(name == self.color)
            rbtn.toggled.connect(self.clickColor)
            rbtn.color = name

            rbtns.addWidget(rbtn)

        detail.addLayout(rbtns)

        btns = QHBoxLayout()

        clear = QPushButton("Clear")
        clear.setStyleSheet("QPushButton{color:black;}")
        clear.clicked.connect(self.clickClear)
        btns.addWidget(clear)

        switch_paraphrase = QPushButton("Hide Paraphrase" if self.show_paraphrase else "Show Paraphrase")
        switch_paraphrase.setStyleSheet("QPushButton{color:black;}")
        switch_paraphrase.clicked.connect(self.clickSwitch)
        btns.addWidget(switch_paraphrase)
        self._switch_paraphrase = switch_paraphrase

        detail.addLayout(btns)
        self._clear = clear

        self.show()

    def clickColor(self, e):
        if e:
            sender = self.sender()
            self.color = sender.color
            self.setWordQss()

    def clickClear(self):
        self.cleared = not self.cleared
        self._clear.setText("Redo" if self.cleared else "Clear")

    def clickSwitch(self):
        self.show_paraphrase = not self.show_paraphrase
        if self.show_paraphrase:
            self._word_label.setText(self._word + " " + self._paraphrase.splitlines()[0])
        else:
            self._word_label.setText(self._word)

        self._switch_paraphrase.setText("Hide Paraphrase" if self.show_paraphrase else "Show Paraphrase")

    def enterWordEvent(self):
        self.setWindowOpacity(1)

    def leaveWordEvent(self):
        if not self._show_detail:
            self.setWindowOpacity(utils.get_setting("danmaku_transparency"))

    def mousePressWordEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._press_point = e.globalPos() - self.pos()
            self._press_start = e.globalPos()
            e.accept()

    def mouseMoveWordEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self.move(e.globalPos() - self._press_point)
            e.accept()

    def mouseReleaseWordEvent(self, e):
        if (e.globalPos() - self._press_start).manhattanLength() < 10:
            self._show_detail = not self._show_detail
            if self._show_detail:
                self._stop_move = True
                self._continenter.show()
            else:
                self._stop_move = False
                self._continenter.hide()
                self.adjustSize()

    def initPosition(self, y):
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.PreciseTimer)
        self._timer.timeout.connect(self.update)
        speed = utils.get_setting("danmaku_speed")
        delta = 1
        while round(delta / speed) < 17:
            delta += 1

        self._timer.start(round(delta / speed))
        self._delta = delta

        w = QDesktopWidget().availableGeometry().width()
        self.move(w, y)

    def update(self):
        if self._stop_move: return
        x = self.x() - self._delta
        self.move(x, self.y())
        if x < -self.width():
            self._timer.stop()
            self.close()
