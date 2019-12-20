from DWords import home

def test_home(qtbot):
    widget = home.Home()
    qtbot.addWidget(widget)

    assert widget.windowTitle() == "DWords"
