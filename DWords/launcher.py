import random
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from .danmuku import Danmuku
from .db import user_db
from . import utils

class Launcher(QObject):
    onChangeWordCleared = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._danmus = set()
        self._burst_words = set()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.newDanmu)
        self._timer.start(utils.get_setting("danmuku_frequency"))

    def newDanmu(self):
        if self._burst_words:
            word = random.choice(list(self._burst_words))
            paraphrase, show_paraphrase, color = user_db.getOne(
                "select paraphrase, show_paraphrase, color from words where word = ?", (word,)
            )
            self._burst_words.remove(word)
        else:
            info = utils.random_one_word(*(danmu._word for danmu in self._danmus))
            if not info: return
            word, paraphrase, show_paraphrase, color = info
            self._timer.setInterval(utils.get_setting("danmuku_frequency"))

        height = QDesktopWidget().availableGeometry().height()
        y = random.randrange(0, int(height / 2))
        danmu = Danmuku(word, paraphrase, y, show_paraphrase, color)
        danmu.onClose.connect(self.onDanmuClose)
        danmu.onModified.connect(self.modifyWord)
        self._danmus.add(danmu)

    def onDanmuClose(self):
        danmu = self.sender()
        self._danmus.remove(danmu)

    def modifyWord(self, attr):
        danmu = self.sender()
        with user_db.cursor() as c:
            c.execute(
                f"update words set {attr} = ? where word = ?",
                (getattr(danmu, attr), danmu._word)
            )

        if attr == "cleared":
            self.onChangeWordCleared.emit(danmu._word)

    def clear(self):
        for danmu in self._danmus:
            danmu.onClose.disconnect(self.onDanmuClose)
            danmu.close()

        self._danmus = set()

    def burst(self):
        if self._burst_words: return

        curr_words = [danmu._word for danmu in self._danmus]
        words = user_db.getAll("select word from words "
            f"where cleared = 0 and word not in ({','.join('?' * len(curr_words))})",
            curr_words
        )
        self._burst_words = set(map(lambda e: e[0], words))
        if not self._burst_words: return

        self._timer.setInterval(700)
