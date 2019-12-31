from functools import wraps
from PyQt5.QtCore import QThread, QObject, pyqtSignal

_coroutines = {}

class Work(QThread):

    def __init__(self, f, args, kw):
        super().__init__()
        self._f = f
        self._args = args
        self._kw = kw

    def run(self):
        try:
            res = self._f(*self._args, *self._kw)
        except Exception as e:
            self.succeed = False
            self.value = e
        else:
            self.succeed = True
            self.value = res

class RunInThread(QObject):

    def __init__(self, f, *args, **kw):
        super().__init__()
        self._thread = Work(f, args, kw)

    def __await__(self):
        self._thread.finished.connect(self.onWorkFinished)
        self._thread.start()
        res = yield self
        return res

    def onWorkFinished(self):
        assert self._thread.isFinished()
        try:
            if self._thread.succeed:
                o = self.co.send(self._thread.value)
            else:
                o = self.co.throw(self._thread.value)
            o.co = self.co
            _coroutines[self.co] = o
        except StopIteration:
            del _coroutines[self.co]

def normal(f):
    @wraps(f)
    def wrapper(*args, **kw):
        co = f(*args, **kw)
        try:
            o = co.send(None)
            o.co = co
            _coroutines[co] = o
        except StopIteration:
            pass

    return wrapper

def thread(f):
    @wraps(f)
    def wrapper(*args, **kw):
        return RunInThread(f, *args, **kw)

    return wrapper
