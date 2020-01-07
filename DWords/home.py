from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QFont, QPixmap, QBrush, QColor, QKeyEvent, QTextCursor
from PyQt5.QtCore import QTimer, Qt, QEvent, pyqtSignal
from .danmaku import Danmaku
from .db import user_db, dictionary_db
from . import utils, real_path
import random

class WordEditor(QTextEdit):
    onCommitWord = pyqtSignal()

    def keyPressEvent(self, e):
        ignore = False
        if e.key() == Qt.Key_Return:
            if e.modifiers() == Qt.ControlModifier:
                self.onCommitWord.emit()
            else:
                text = self.toPlainText()
                if "\n" not in text:
                    paraphrase = utils.consult(text)
                    if paraphrase:
                        self.setPlainText(text + "\n" + paraphrase)
                        cursor = self.textCursor()
                        start = cursor.position() + len(text) + 1
                        end = len(self.toPlainText())
                        cursor.setPosition(start, QTextCursor.MoveAnchor)
                        cursor.setPosition(end, QTextCursor.KeepAnchor)
                        self.setTextCursor(cursor)

                        ignore = True

        if not ignore:
            super().keyPressEvent(e)

class Home(QWidget):
    onClickBurst = pyqtSignal()
    onClickSetting = pyqtSignal()
    onClickSync = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._closing = False
        self._is_hid_paraphrase = False
        self._list_order = 'Time'

        self.initUI()

        self.show()

    def initUI(self):
        self.setWindowTitle("DWords")
        self.setWindowIcon(QIcon(real_path("img/logo.svg")))
        self.setMinimumWidth(400)

        body = QVBoxLayout()
        self.setLayout(body)

        head = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(
            QPixmap(real_path("img/logo.svg"))
            .scaled(50, 50, transformMode=Qt.SmoothTransformation)
        )
        head.addWidget(icon)

        title = QLabel("DWords")
        title.setFont(QFont("Consolas", 18))
        title.font().setStyleStrategy(QFont.PreferAntialias)
        head.addWidget(title)
        head.addStretch(1)
        body.addLayout(head)
        body.addSpacing(8)

        lists = QTabWidget()
        lists.setMinimumHeight(300)

        def create_list():
            tree = QTreeWidget()
            tree.setContextMenuPolicy(Qt.CustomContextMenu)
            tree.customContextMenuRequested.connect(self.listMenu)
            tree.itemClicked.connect(self.clickList)
            tree.itemDoubleClicked.connect(self.doubleClickList)
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
        burst.clicked.connect(self.clickBurst)
        setting = QPushButton("Setting")
        setting.clicked.connect(self.clickSetting)
        sync = QPushButton("Sync")
        sync.clicked.connect(self.clickSync)
        self.sync_btn = sync

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

        word_editor = WordEditor()
        word_editor.setMinimumHeight(100)
        word_editor.onCommitWord.connect(self.commitWord)
        layout.addWidget(word_editor)
        self._word_editor = word_editor

        commit = QPushButton("Commit")
        commit.clicked.connect(self.commitWord)
        close = QPushButton("Close")
        close.clicked.connect(self.clickCloseEditor)

        btns = QHBoxLayout()
        btns.addStretch(1)
        btns.addWidget(commit)
        btns.addWidget(close)

        layout.addLayout(btns)

        return editor

    def showEditor(self, word=None, paraphrase=None):
        self._editor.show()
        if word is not None and paraphrase is not None:
            self._word_editor.setText(word + '\n' + paraphrase)

    def hideEditor(self):
        self._editor.hide()
        self._word_editor.clear()

    def commitWord(self):
        text = self._word_editor.toPlainText()
        while True:
            if len(text) == 0: break

            word, *paraphrase = text.splitlines()
            paraphrase = '\n'.join(paraphrase)
            if len(word) == 0 or len(paraphrase) == 0: break

            utils.add_words((word, paraphrase))
            self.initLists()

            break

        self._word_editor.clear()

    def clickCloseEditor(self):
        self.hideEditor()
        # self.adjustSize()

    def clickBurst(self):
        self.onClickBurst.emit()

    def clickSetting(self):
        self.onClickSetting.emit()

    def clickSync(self):
        self.onClickSync.emit()

    def initLists(self):
        def create_item(word, paraphrase, cleared):
            item = QTreeWidgetItem()
            item.setText(0, word)
            item.setText(1, '' if self._is_hid_paraphrase else paraphrase.splitlines()[0])
            item.setToolTip(1, '' if self._is_hid_paraphrase else paraphrase)
            item.cleared = cleared
            item.paraphrase = paraphrase
            if cleared:
                item.setForeground(0, QBrush(QColor(0x27ae60)))
                item.setForeground(1, QBrush(QColor(0x27ae60)))
            return item

        if self._list_order == "A-Z":
            order_by = "order by word"
        elif self._list_order == "Time":
            order_by = "order by time desc, word"

        self._curr_words.clear()
        for word, paraphrase in user_db.getAll("select word, paraphrase from words where cleared = 0 " + order_by):
            self._curr_words.addTopLevelItem(create_item(word, paraphrase, False))

        self._cleared_words.clear()
        for word, paraphrase in user_db.getAll("select word, paraphrase from words where cleared = 1 " + order_by):
            self._cleared_words.addTopLevelItem(create_item(word, paraphrase, True))

        self._all_words.clear()
        for info in user_db.getAll("select word, paraphrase, cleared from words " + order_by):
            self._all_words.addTopLevelItem(create_item(*info))

    def clickOrder(self, e):
        if e:
            rbtn = self.sender()
            self._list_order = rbtn.text()
            self.initLists()

    def clickList(self, item):
        if not self._is_hid_paraphrase: return
        if item.text(1) == '':
            item.setText(1, item.paraphrase.splitlines()[0])
            item.setToolTip(1, item.paraphrase)
        else:
            item.setText(1, '')
            item.setToolTip(1, '')

    def doubleClickList(self, item):
        if self._is_hid_paraphrase: return
        self.showEditor(item.text(0), item.paraphrase)

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
        menu.paraphrase = item.paraphrase
        menu.addAction("Edit").triggered.connect(self.clickMenu)
        menu.addAction("Redo" if item.cleared else "Clear").triggered.connect(self.clickMenu)
        menu.addAction("Delete").triggered.connect(self.clickMenu)
        menu.exec(list_.mapToGlobal(pos))

    def clickMenu(self):
        action = self.sender()
        act = action.text()
        word = action.parent().word
        paraphrase = action.parent().paraphrase
        refresh = False
        if act == "Edit":
            self.showEditor(word, paraphrase)
        elif act == "Clear":
            utils.set_word_attribute(word, cleared=True)
            refresh = True
        elif act == "Redo":
            utils.set_word_attribute(word, cleared=False)
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
        self.showEditor()

    def closeEvent(self, e):
        self.hide()
        e.ignore()
