from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QPixmap, QBrush, QColor
from PyQt5.QtCore import QTimer, Qt, QEvent, pyqtSignal
from danmuku import Danmuku
from db import user_db
import random
import utils

class Home(QWidget):
    def __init__(self):
        super().__init__()
        self._danmus = set()
        self._closing = False
        self._is_hid_paraphrase = False

        self.initUI()

        self.show()
        self.activateWindow()

    def initUI(self):
        self.setGeometry(300, 300, 500, 300)
        self.setWindowTitle("DWords")
        self.setWindowIcon(QIcon("img/logo.svg"))

        body = QVBoxLayout()
        self.setLayout(body)

        head = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(QPixmap("img/logo.svg").scaled(50, 50, transformMode=Qt.SmoothTransformation))
        head.addWidget(icon)

        title = QLabel("DWords")
        title.setFont(QFont("Consolas", 24))
        head.addWidget(title)
        head.addStretch(1)
        body.addLayout(head)

        lists = QTabWidget()
        lists.setMinimumHeight(300)

        def create_list():
            tree = QTreeWidget()
            tree.setContextMenuPolicy(Qt.CustomContextMenu)
            tree.customContextMenuRequested.connect(self.listMenu)
            tree.itemClicked.connect(self.clickList)
            tree.setColumnCount(2)
            tree.setHeaderLabels(["Word", "Paraphrase"])
            return tree

        self._curr_words = create_list()
        self._cleared_words = create_list()
        self._all_words = create_list()
        self.initLists()

        lists.addTab(self._curr_words, "Current Words")
        lists.addTab(self._cleared_words, "Cleared Words")
        lists.addTab(self._all_words, "All Words")
        body.addWidget(lists)

        list_btns = QHBoxLayout()
        add = QPushButton("+")
        add.setFixedWidth(22)
        add.clicked.connect(self.clickAdd)
        hide_paraphrase = QCheckBox("Hide Paraphrase")
        hide_paraphrase.toggled.connect(self.clickHideParaphrase)
        order_by_time = QRadioButton("Time")
        order_by_time.setChecked(True)
        order_by_time.toggled.connect(self.clickOrder)
        order_by_word = QRadioButton("A-Z")
        order_by_word.toggled.connect(self.clickOrder)

        list_btns.addWidget(add)
        list_btns.addWidget(hide_paraphrase)
        list_btns.addStretch(1)
        list_btns.addWidget(QLabel("Order By:"))
        list_btns.addWidget(order_by_time)
        list_btns.addWidget(order_by_word)

        body.addLayout(list_btns)

        burst = QPushButton("Burst!")
        setting = QPushButton("Setting")
        sync = QPushButton("Sync")

        btns = QHBoxLayout()
        btns.addStretch(1)
        btns.addWidget(burst)
        btns.addWidget(sync)
        btns.addWidget(setting)

        body.addLayout(btns)

        self._editor = self.setEditor()
        body.addWidget(self._editor)

    def setEditor(self):
        editor = QWidget(self)
        editor.hide()
        layout = QVBoxLayout()
        editor.setLayout(layout)

        text = QTextEdit()
        text.setMinimumHeight(100)
        layout.addWidget(text)

        commit = QPushButton("Commit")
        close = QPushButton("Close")
        close.clicked.connect(self.clickCloseEditor)

        btns = QHBoxLayout()
        btns.addStretch(1)
        btns.addWidget(commit)
        btns.addWidget(close)

        layout.addLayout(btns)

        return editor

    def clickCloseEditor(self):
        self._editor.hide()

    def initLists(self, order="Time"):
        def create_item(word, paraphrase, cleared):
            item = QTreeWidgetItem()
            item.setText(0, word)
            item.setText(1, paraphrase.splitlines()[0])
            item.setToolTip(1, paraphrase)
            item.cleared = cleared
            item.paraphrase = paraphrase
            if cleared:
                item.setForeground(0, QBrush(QColor(0x27ae60)))
                item.setForeground(1, QBrush(QColor(0x27ae60)))
            return item

        if order == "A-Z":
            order_by = "order by word"
        elif order == "Time":
            order_by = "order by id desc"

        self._curr_words.clear()
        for word, paraphrase in user_db.getAll("select word, paraphrase from words where cleared = false " + order_by):
            self._curr_words.addTopLevelItem(create_item(word, paraphrase, False))

        self._cleared_words.clear()
        for word, paraphrase in user_db.getAll("select word, paraphrase from words where cleared = true " + order_by):
            self._cleared_words.addTopLevelItem(create_item(word, paraphrase, True))

        self._all_words.clear()
        for info in user_db.getAll("select word, paraphrase, cleared from words " + order_by):
            self._all_words.addTopLevelItem(create_item(*info))

    def clickOrder(self, e):
        if e:
            rbtn = self.sender()
            self.initLists(rbtn.text())

    def clickList(self, item):
        if not self._is_hid_paraphrase: return
        if item.text(1) == '':
            item.setText(1, item.paraphrase.splitlines()[0])
            item.setToolTip(1, item.paraphrase)
        else:
            item.setText(1, '')
            item.setToolTip(1, '')

    def clickHideParaphrase(self, e):
        self._is_hid_paraphrase = e
        for list_ in (self._curr_words, self._cleared_words, self._all_words):
            it = QTreeWidgetItemIterator(list_)
            while it.value():
                item = it.value()
                item.setText(1, '' if e else item.paraphrase.splitlines()[0])
                item.setToolTip(1, '' if e else item.paraphrase)
                it += 1

    def listMenu(self, pos):
        list_ = self.sender()
        item = list_.itemAt(pos)
        if not item: return

        menu = QMenu(self)
        menu.word = item.text(0)
        menu.addAction("Detail").triggered.connect(self.clickMenu)
        menu.addAction("Redo" if item.cleared else "Clear").triggered.connect(self.clickMenu)
        menu.addAction("Delete").triggered.connect(self.clickMenu)
        menu.exec(list_.mapToGlobal(pos))

    def clickMenu(self):
        action = self.sender()
        act = action.text()
        word = action.parent().word
        refresh = False
        if act == "Clear":
            utils.clear_words(word)
            refresh = True
        elif act == "Redo":
            utils.redo_words(word)
            refresh = True
        elif act == "Delete":
            reply = QMessageBox.question(
                self, 'Tips', "Are you sure you want to delete this word?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                utils.delete_words(word)
                refresh = True

        if refresh:
            self.initLists()

    def clickAdd(self):
        self._editor.show()

    def closeEvent(self, e):
        self.hide()
        self._editor.close()
        e.ignore()
