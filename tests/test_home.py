import uuid
from PyQt5.QtCore import Qt
from DWords import home
from DWords.db import user_db

def test_home(qtbot):
    widget = home.Home()
    qtbot.addWidget(widget)

    assert widget.windowTitle() == "DWords"

def test_add_word(qtbot):
    widget = home.Home()
    qtbot.addWidget(widget)

    add = widget.layout().itemAt(3).itemAt(0).widget()
    assert add.text() == "+"
    qtbot.mouseClick(add, Qt.LeftButton)

    assert widget._word_editor.isVisible() == True

    word = str(uuid.uuid1())
    paraphrase = str(uuid.uuid1())
    widget._word_editor.setPlainText(word + "\n" + paraphrase)

    commit = widget._editor.layout().itemAt(1).itemAt(1).widget()
    assert commit.text() == "Commit"

    qtbot.mouseClick(commit, Qt.LeftButton)
    res, = user_db.getOne("select paraphrase from words where word = ?", (word,))
    assert res == paraphrase

    close = widget._editor.layout().itemAt(1).itemAt(2).widget()
    assert close.text() == "Close"
    qtbot.mouseClick(close, Qt.LeftButton)
    assert widget._word_editor.isVisible() == False
