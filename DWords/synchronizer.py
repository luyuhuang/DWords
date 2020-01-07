import logging
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
        self._mail = Mail()
        self._synchronizing = False
        self._add_count = 0
        self._del_count = 0

    async def _sync(self):
        async with self.connect():
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

            await self.publish(words)

            with user_db.cursor() as c:
                c.execute("delete from sync_cache")

            words = await self.collect()

            for word, (op, time, data) in words.items():
                modify_time = user_db.getOne("select modify_time from words where word = ?", (word,))
                if not modify_time or time > modify_time[0]:
                    self.accept(word, op, time, data)

            self.onSynchronizeDone.emit()
            logging.info(f"Add {self._add_count} word(s) and delete {self._del_count} word(s)")

    async def sync(self):
        assert not self._synchronizing, "Synchronizing"
        self._synchronizing = True

        try:
            await self._sync()
        finally:
            self._synchronizing = False
            self._add_count, self._del_count = 0, 0

    def connect(self):
        return self._mail.connect()

    async def publish(self, words):
        if not words: return
        await self._mail.push(self.UUID, words)

    async def collect(self):
        word_time_map = {}
        ans = {}
        async for words in self._mail.pull(self.UUID):
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

                self._add_count += 1

        elif op == "del":
            with user_db.cursor() as c:
                c.execute("delete from words where word = ?", (word,))

                self._del_count += 1
