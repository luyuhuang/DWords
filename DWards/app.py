from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QCoreApplication
from home import Home
from launcher import Launcher
from db import user_db, initialize

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        initialize()
        self._launcher = Launcher()
        self._home = Home()

        self.setQuitOnLastWindowClosed(False)
        self.setTrayIcon()

    def setTrayIcon(self):
        tray_icon = QSystemTrayIcon(QIcon("img/logo.svg"), self)
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
        pass

    def clickSetting(self):
        pass

    def clickExit(self):
        self._launcher.close()
        user_db.close()
        self.quit()
