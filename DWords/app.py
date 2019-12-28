from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QCoreApplication
from .home import Home
from .launcher import Launcher
from .synchronizer import Synchronizer
from .setting import Setting
from .db import user_db, initialize
from . import real_path

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        initialize()
        self._launcher = Launcher()
        self._synchronizer = Synchronizer()
        self._home = Home()
        self._setting = None

        self._home.onClickBurst.connect(self.clickBurst)
        self._home.onClickSetting.connect(self.clickSetting)
        self._home.onClickSync.connect(self.clickSync)
        self._launcher.onChangeWordCleared.connect(self._home.initLists)
        self._synchronizer.onSynchronizeDone.connect(self._home.initLists)

        self.setQuitOnLastWindowClosed(False)
        self.setTrayIcon()

    def setTrayIcon(self):
        tray_icon = QSystemTrayIcon(QIcon(real_path("img/logo.svg")), self)
        tray_icon.show()
        menu = QMenu()
        menu.addAction("Burst!").triggered.connect(self.clickBurst)
        menu.addAction("Sync").triggered.connect(self.clickSync)
        menu.addAction("Setting").triggered.connect(self.clickSetting)
        menu.addAction("Exit").triggered.connect(self.clickExit)
        tray_icon.setContextMenu(menu)
        tray_icon.activated.connect(self.clickTrayIcon)
        tray_icon.setToolTip("DWords")

    def clickTrayIcon(self, e):
        if e == QSystemTrayIcon.Trigger:
            self._home.showNormal()
            self._home.show()
            self._home.activateWindow()

    def clickBurst(self):
        self._launcher.burst()

    def clickSync(self):
        # try:
        self._synchronizer.sync()
        # except Exception as e:
        #     QMessageBox.critical(self._home, "Error", str(e), QMessageBox.Yes)

    def clickSetting(self):
        if self._setting:
            self._setting.showNormal()
            self._setting.activateWindow()
        else:
            self._setting = Setting()
            self._setting.destroyed.connect(self.onSettingClose)

    def onSettingClose(self):
        self._setting = None

    def clickExit(self):
        self._launcher.clear()
        user_db.close()
        self.quit()
