import random
import uuid
from PyQt5.QtCore import Qt
from DWords import danmaku
from DWords import utils
from DWords.launcher import Launcher
from DWords.db import user_db

def test_add_words():
    utils.add_words(
        (str(uuid.uuid1()), str(uuid.uuid1())),
        (str(uuid.uuid1()), str(uuid.uuid1())),
    )

def test_danmaku(qtbot):
    word, paraphrase, _, color = utils.random_one_word()
    widget = danmaku.Danmaku(word, paraphrase, random.randrange(0, 200), False, color)
    qtbot.addWidget(widget)

    assert widget._word_label.text() == word

def test_danmaku_with_paraphrase(qtbot):
    word, paraphrase, _, color = utils.random_one_word()
    widget = danmaku.Danmaku(word, paraphrase, random.randrange(0, 200), True, color)
    qtbot.addWidget(widget)

    assert widget._word_label.text() ==  word + " " + paraphrase

def test_danmaku_panel(qtbot):
    word, paraphrase, _, color = utils.random_one_word()
    widget = danmaku.Danmaku(word, paraphrase, random.randrange(0, 200), True, color)
    qtbot.addWidget(widget)

    assert widget._continenter.isVisible() == False
    qtbot.mouseClick(widget._word_label, Qt.LeftButton)
    assert widget._continenter.isVisible() == True
    qtbot.mouseClick(widget._word_label, Qt.LeftButton)
    assert widget._continenter.isVisible() == False

def test_danmaku_clear(qtbot):
    word, paraphrase, _, color = utils.random_one_word()
    widget = danmaku.Danmaku(word, paraphrase, random.randrange(0, 200), True, color)
    qtbot.addWidget(widget)

    launcher = Launcher()
    widget.onModified.connect(launcher.modifyWord)

    assert widget._continenter.isVisible() == False
    qtbot.mouseClick(widget._word_label, Qt.LeftButton)
    assert widget._continenter.isVisible() == True

    qtbot.mouseClick(widget._clear, Qt.LeftButton)
    cleared, = user_db.getOne("select cleared from words where word = ?", (word,))
    assert cleared
