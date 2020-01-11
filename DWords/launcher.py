import random
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from .danmaku import Danmaku
from .db import user_db
from . import utils

class Launcher(QObject):
    onChangeWordCleared = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._danmakus = {}
        self._burst_words = set()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.newDanmaku)
        self._timer.start(utils.get_setting("danmaku_frequency"))

    def newDanmaku(self):
        if self._burst_words:
            word = random.choice(list(self._burst_words))
            paraphrase, show_paraphrase, color = user_db.getOne(
                "select paraphrase, show_paraphrase, color from words where word = ?", (word,)
            )
            self._burst_words.remove(word)
        else:
            info = utils.random_one_word(*self._danmakus.keys())
            if not info: return
            word, paraphrase, show_paraphrase, color = info
            self._timer.setInterval(utils.get_setting("danmaku_frequency"))

        height = QDesktopWidget().availableGeometry().height()
        y = random.randrange(0, int(height / 2))

        def onDanmaClose():
            del self._danmakus[word]

        danmaku = Danmaku(word, paraphrase, y, show_paraphrase, color)
        danmaku.destroyed.connect(onDanmaClose)
        danmaku.onModified.connect(self.modifyWord)
        self._danmakus[word] = danmaku

    def modifyWord(self, attr):
        danmaku = self.sender()
        utils.set_word_attribute(danmaku._word, **{attr: getattr(danmaku, attr)})

        if attr == "cleared":
            self.onChangeWordCleared.emit(danmaku._word)

    def clear(self):
        for danmaku in self._danmakus.values():
            danmaku.destroyed.disconnect()
            danmaku.close()

        self._danmakus = {}

    def burst(self):
        if self._burst_words: return

        curr_words = list(self._danmakus.keys())
        words = user_db.getAll("select word from words "
            f"where cleared = 0 and word not in ({','.join('?' * len(curr_words))})",
            curr_words
        )
        self._burst_words = set(map(lambda e: e[0], words))
        if not self._burst_words: return

        self._timer.setInterval(1500)
