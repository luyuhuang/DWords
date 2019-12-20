import random
from DWords import danmuku

def test_danmuku(qtbot):
    widget = danmuku.Danmuku("apple", "苹果", random.randrange(0, 200))
    qtbot.addWidget(widget)

    assert widget._word_label.text() == "apple"

def test_danmuku_with_paraphrase(qtbot):
    widget = danmuku.Danmuku("apple", "苹果", random.randrange(0, 200), True)
    qtbot.addWidget(widget)

    assert widget._word_label.text() == "apple 苹果"
