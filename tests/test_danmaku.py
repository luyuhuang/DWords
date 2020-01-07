import random
from DWords import danmaku

def test_danmaku(qtbot):
    widget = danmaku.Danmaku("apple", "苹果", random.randrange(0, 200))
    qtbot.addWidget(widget)

    assert widget._word_label.text() == "apple"

def test_danmaku_with_paraphrase(qtbot):
    widget = danmaku.Danmaku("apple", "苹果", random.randrange(0, 200), True)
    qtbot.addWidget(widget)

    assert widget._word_label.text() == "apple 苹果"
