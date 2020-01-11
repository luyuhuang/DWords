import os
import uuid
import time
import poplib
from PyQt5.QtCore import QThread
from DWords.synchronizer import Synchronizer
from DWords.db import user_db
from DWords import utils
from DWords import async_thread

def test_set_account():
    utils.set_setting("email", os.environ["MAIL_ADDR"])
    utils.set_setting("password", os.environ["MAIL_PASSWORD"])
    utils.set_setting("smtp_server", os.environ["SMTP_SERVER"])
    utils.set_setting("pop3_server", os.environ["POP3_SERVER"])

def test_add_words():
    utils.add_words(
        (str(uuid.uuid1()), str(uuid.uuid1())),
        (str(uuid.uuid1()), str(uuid.uuid1())),
    )

@async_thread.normal
async def _sync():
    synchronizer = Synchronizer()
    await synchronizer.sync()

def _delete_mails():
    pop3_server = utils.get_setting("pop3_server")
    email = utils.get_setting("email")
    password = utils.get_setting("password")

    pop3 = poplib.POP3_SSL(pop3_server, poplib.POP3_SSL_PORT, timeout=30)
    pop3.user(email)
    pop3.pass_(password)

    count, _ = pop3.stat()
    for i in range(1, count + 1):
        pop3.dele(i)

    pop3.quit()

def test_sync(qtbot):
    _delete_mails()

    num, = user_db.getOne("select count(*) from sync_cache where op = 'add'")

    _sync()
    qtbot.waitUntil(lambda: not async_thread._coroutines, timeout=30000)
    assert user_db.getOne("select count(*) from sync_cache")[0] == 0

    with user_db.cursor() as c:
        c.execute("delete from words")
        c.execute("delete from sys where id = 'last_mail_id'")
        c.execute("update sys set value = ? where id = 'uuid'", (str(uuid.uuid1()),))

    _sync()
    qtbot.waitUntil(lambda: not async_thread._coroutines, timeout=30000)
    assert user_db.getOne("select count(*) from words")[0] == num
