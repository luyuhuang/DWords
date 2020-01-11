import json
import poplib
import smtplib
import poplib
import logging
from html_text import extract_text
from email import encoders, policy
from email.header import Header, decode_header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.parser import Parser, FeedParser
from dateutil.parser import parse as parse_timestr
from . import utils
from .db import user_db
from .async_thread import thread

class Mail:
    def __init__(self):
        pass

    async def __aenter__(self):
        logging.debug("Connecting...")
        await self._connect()
        logging.debug("Connected")

    async def __aexit__(self, type, value, tb):
        self._smtp.quit()
        self._pop3.quit()
        del self._smtp
        del self._pop3
        logging.debug("Disconnected")

    @thread
    def _connect(self):
        self._smtp = smtplib.SMTP_SSL(self._smtp_server, smtplib.SMTP_SSL_PORT, timeout=30)
        self._smtp.helo(self._smtp_server)
        self._smtp.ehlo(self._smtp_server)
        self._smtp.login(self._email, self._password)
        self._pop3 = poplib.POP3_SSL(self._pop3_server, poplib.POP3_SSL_PORT, timeout=30)
        self._pop3.user(self._email)
        self._pop3.pass_(self._password)

    def connect(self):
        self._smtp_server = utils.get_setting("smtp_server")
        self._pop3_server = utils.get_setting("pop3_server")
        self._email = utils.get_setting("email")
        self._password = utils.get_setting("password")

        if None in (self._smtp_server, self._pop3_server, self._email, self._password):
            raise Exception("Incomplete email setting")

        return self

    @thread
    def _push(self, uuid, words):
        subject = "DWords synchronize"
        content = json.dumps(words)

        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = f"{uuid}<{self._email}>"
        msg["Subject"] = subject
        msg["To"] = self._email

        self._smtp.sendmail(self._email, [self._email], msg.as_string())

    async def push(self, uuid, words):
        logging.debug("Pushing...")
        await self._push(uuid, words)
        logging.info(f"{len(words)} word(s) pushed")

    def _decode_str(self, s):
        value, charset = decode_header(s)[0]
        if charset:
            value = value.decode(charset)
        return value

    def _guess_charset(self, msg):
        charset = msg.get_charset()
        if charset is None:
            content_type = msg.get('Content-Type', '').lower()
            pos = content_type.find('charset=')
            if pos >= 0:
                charset = content_type[pos + 8:].strip()

        return charset

    def _parse_content(self, msg):
        content_type = msg.get_content_type()
        if content_type == "multipart/alternative":
            plain, html = None, None
            for part in msg.get_payload():
                ct = part.get_content_type()
                if ct == "text/plain":
                    plain = part
                    break
                elif ct == "text/html":
                    html = part

            if plain:
                return self._parse_content(plain)
            elif html:
                return self._parse_content(html)

        elif content_type == "text/plain":
            content = msg.get_payload(decode=True)
            charset = self._guess_charset(msg)
            if charset:
                content = content.decode(charset)

            return content

        elif content_type == "text/html":
            content = msg.get_payload(decode=True)
            charset = self._guess_charset(msg)
            if charset:
                content = content.decode(charset)

            return extract_text(content)

    @thread
    def _pop3_stat(self):
        return self._pop3.stat()

    @thread
    def _pop3_retr(self, i):
        return self._pop3.retr(i)

    async def pull(self, uuid):
        logging.debug("Getting mail count...")
        count, _ = await self._pop3_stat()
        logging.debug(f"Mail count: {count}")
        last_id = user_db.getOne("select value from sys where id = 'last_mail_id'")
        if last_id:
            last_id, = last_id

        get_count, read_count = 0, 0
        for i in range(count, max(0, count - 50), -1):
            logging.debug(f"Retrieving mail {i}")
            _, lines, _ = await self._pop3_retr(i)
            msg = Parser(policy=policy.default).parsestr(b"\n".join(lines).decode("utf-8"))

            try:
                msg_id = msg.get("Message-Id")
            except Exception as e:
                logging.warning(f"Error getting Message-Id. The mail[{i}] is ignored. Error message: {e}")
                continue

            logging.debug(f"Got mail: {msg_id}")
            get_count += 1

            if msg_id == last_id: break
            if i == count:
                with user_db.cursor() as c:
                    c.execute("update sys set value = ? where id = 'last_mail_id'", (msg_id,))
                    c.execute("insert or ignore into sys(id, value) values('last_mail_id', ?)", (msg_id,))

            subject = msg.get("Subject")
            if not subject: continue
            subject = self._decode_str(subject)
            if not subject.startswith("DWords"): continue

            if subject == "DWords synchronize":
                from_id, email = parseaddr(msg.get("From"))
                from_id = self._decode_str(from_id)
                if from_id != uuid and email == self._email:
                    content = self._parse_content(msg)
                    try:
                        words = json.loads(content)
                        yield words
                        read_count += 1
                    except:
                        pass

            elif subject == "DWords add":
                time = int(parse_timestr(msg.get("Date")).timestamp() * 1000)
                content = self._parse_content(msg)
                word, paraphrase = "", []
                tostr = lambda w, p: "\n".join(p) if p else utils.consult(w) or "<None>"
                words = {}
                for line in content.splitlines():
                    line = line.strip()
                    if not line: continue
                    if line.startswith("~~~") or line.startswith("..."):
                        break
                    elif line.startswith("---") or line.startswith(",,,"):
                        if word:
                            words[word] = ("add", time, {"paraphrase": tostr(word, paraphrase)})
                        word, paraphrase = "", []
                    else:
                        if not word:
                            word = line
                        else:
                            paraphrase.append(line)
                if word:
                    words[word] = ("add", time, {"paraphrase": tostr(word, paraphrase)})

                yield words
                read_count += 1

        logging.debug(f"Got {get_count} mail(s) and accepted {read_count} mail(s)")
