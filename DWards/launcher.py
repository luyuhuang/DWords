import utils
import random
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtCore import QTimer, QObject
from danmuku import Danmuku
from db import user_db

class Launcher(QObject):
    def __init__(self):
        super().__init__()
        self._danmus = set()
        self._closing = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.newDanmu)
        self._timer.start(6000)

    def newDanmu(self):
        info = utils.random_one_word(*(danmu._word for danmu in self._danmus))
        if not info: return
        word, paraphrase, show_paraphrase, color = info

        height = QDesktopWidget().availableGeometry().height()
        y = random.randrange(0, height / 2)
        danmu = Danmuku(word, paraphrase, y, show_paraphrase, color)
        danmu.onCloseDanmu.connect(self.onDanmuClose)
        self._danmus.add(danmu)

    def onDanmuClose(self):
        danmu = self.sender()

        with user_db.cursor() as c:
            c.execute("update words "
                "set show_paraphrase = ?, color = ?, cleared = ? "
                "where word = ?",
                (danmu._show_paraphrase, danmu._color, danmu._cleared, danmu._word)
            )

        if not self._closing:
            self._danmus.remove(danmu)

    def close(self):
        self._closing = True
        for danmu in self._danmus:
            danmu.close()

    def burst(self):
        pass
