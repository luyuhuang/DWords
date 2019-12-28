from PyQt5.QtCore import QObject, pyqtSignal
from . import utils
from .mail import Mail
from .db import user_db

class Synchronizer(QObject):
    FIELDS = ["time", "paraphrase", "show_paraphrase", "color", "cleared"]
    onSynchronizeDone = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.UUID, = user_db.getOne("select value from sys where id = 'uuid'")
        self._mail = None

    def get_mail(self):
        if self._mail is None:
            self._mail = Mail()

        return self._mail

    def close_mail(self):
        if self._mail:
            self._mail.close()
        self._mail = None

    def sync(self):
        cache = user_db.getAll("select word, op, time from sync_cache")
        words = {}
        for word, op, time in cache:
            if op == "add":
                values = user_db.getOne(f"select {','.join(self.FIELDS)} from words "
                    "where word = ?", (word,))

                data = dict(zip(self.FIELDS, values))
                words[word] = ("add", time, data)
            elif op == "del":
                words[word] = ("del", time, None)

        self.publish(words)

        with user_db.cursor() as c:
            c.execute("delete from sync_cache")

        for word, (op, time, data) in self.collect().items():
            modify_time = user_db.getOne("select modify_time from words where word = ?", (word,))
            if not modify_time or time > modify_time[0]:
                self.accept(word, op, time, data)

        print("Synchronize done")
        self.onSynchronizeDone.emit()

    def publish(self, words):
        if not words: return
        self.get_mail().push(self.UUID, words)

    def collect(self):
        word_time_map = {}
        ans = {}
        for words in self.get_mail().pull(self.UUID + "a"):
            for word, (op, time, data) in words.items():
                if time > word_time_map.get(word, 0):
                    word_time_map[word] = time
                    ans[word] = (op, time, data)

        return ans

    def accept(self, word, op, time, data):
        if op == "add":
            keys, values = zip(*data.items())
            with user_db.cursor() as c:
                sql = "update words set " + \
                    ",".join(key + "=?" for key in keys) + \
                    ", modify_time = ? where word = ?"
                c.execute(sql, values + (time, word))

                sql = "insert or ignore into words(word, modify_time, " + \
                    ",".join(keys) + ")" + \
                    " values(?,?," + ",".join("?" * len(keys)) + ")"
                c.execute(sql, (word, time) + values)

        elif op == "del":
            with user_db.cursor() as c:
                c.execute("delete from words where word = ?", word)
