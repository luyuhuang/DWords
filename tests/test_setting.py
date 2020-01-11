from DWords.setting import Setting

def test_setting(qtbot):
    widget = Setting()
    qtbot.addWidget(widget)

    assert widget.windowTitle() == "DWords - Setting"
