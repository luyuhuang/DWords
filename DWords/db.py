import sqlite3
import uuid
import os
from contextlib import contextmanager
from .version import VERSIONs
from .migrate import SQLs
from . import real_path

class DB:
    def __init__(self, database):
        self._conn = sqlite3.connect(database)
        self._in_cursor = False

    def getOne(self, sql, param=()):
        assert not self._in_cursor, "Cannot call get in cursor"
        cursor = self._conn.execute(sql, param)
        res = cursor.fetchone()
        cursor.close()
        self._conn.rollback()
        return res

    def getAll(self, sql, param=()):
        assert not self._in_cursor, "Cannot call get in cursor"
        cursor = self._conn.execute(sql, param)
        res = cursor.fetchall()
        cursor.close()
        self._conn.rollback()
        return res

    @contextmanager
    def cursor(self):
        assert not self._in_cursor, "Cannot nest open cursor"
        try:
            self._in_cursor = True
            cursor = self._conn.cursor()
            yield cursor
        except:
            self._conn.rollback()
            raise
        else:
            self._conn.commit()
        finally:
            cursor.close()
            self._in_cursor = False

    def close(self):
        self._conn.close()

if os.name == "nt":
    data_dir = os.path.join(os.environ["USERPROFILE"], ".DWords")
else:
    data_dir = os.path.join(os.environ["HOME"], ".DWords")

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

user_db = DB(os.path.join(data_dir, "user.db"))
dictionary_db = DB(real_path("data/dictionary.db"))

def initialize():
    if not user_db.getOne("select * from sqlite_master where type = 'table' and name = 'sys'"):
        with user_db.cursor() as c:
            c.executescript(f"""
            create table sys (
                id varchar(128) primary key,
                value text not null default ''
            );
            insert into sys values('version', '-1');
            insert into sys values('uuid', '{uuid.uuid1()}');
            """)

    version, = map(int, user_db.getOne("select value from sys where id = 'version'"))
    with user_db.cursor() as c:
        for v in VERSIONs[version + 1:]:
            if v in SQLs:
                c.executescript(SQLs[v])

        c.execute("update sys set value = ? where id = 'version'", (len(VERSIONs) - 1,))

