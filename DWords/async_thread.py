from PyQt5.QtCore import QThread, QObject, pyqtSignal

class Work(QThread):
    workSucceed = pyqtSignal(object)
    workFailed = pyqtSignal(Exception)

    def __init__(self, f, args, kw):
        super().__init__()
        self._f = f
        self._args = args
        self._kw = kw

    def run(self):
        try:
            res = self._f(*self._args, *self._kw)
        except Exception as e:
            self.workFailed.emit(e)
        else:
            self.workSucceed.emit(res)

class RunInThread(QObject):

    def __init__(self, f, *args, **kw):
        super().__init__()
        self._thread = Work(f, args, kw)

    def __await__(self):
        self._thread.start()
        self._thread.workSucceed.connect(self.onSucceed)
        self._thread.workFailed.connect(self.onFailed)
        res = yield self
        return res

    def onSucceed(self, res):
        try:
            o = self.co.send(res)
            o.co = self.co
        except StopIteration:
            pass

    def onFailed(self, err):
        try:
            o = self.co.throw(err)
            o.co = self.co
        except StopIteration:
            pass

def normal(f):
    def wrapper(*args, **kw):
        co = f(*args, **kw)
        try:
            o = co.send(None)
            o.co = co
        except StopIteration:
            pass

    return wrapper