from db import user_db

COLORS = {
    'red': ("231,76,60", "255,255,255"),
    'yellow': ("241,196,15", "255,255,255"),
    'orange': ("243,156,18", "255,255,255"),
    'cyan': ("26,188,156", "255,255,255"),
    'green': ("46,204,113", "255,255,255"),
    'blue': ("52,152,219", "255,255,255"),
    'purple': ("155,89,182", "255,255,255"),
    'white': ("236,240,241", "0,0,0"),
}

def clear_words(*words):
    with user_db.cursor() as c:
        c.execute(f"update words set cleared = 1 where word in ({','.join('?' * len(words))})", words)

def redo_words(*words):
    with user_db.cursor() as c:
        c.execute(f"update words set cleared = 0 where word in ({','.join('?' * len(words))})", words)

def delete_words(*words):
    with user_db.cursor() as c:
        c.execute(f"delete from words where word in ({','.join('?' * len(words))})", words)

def random_one_word(*exceptions):
    return user_db.getOne("select word, paraphrase, show_paraphrase, color "
        "from words where cleared = 0 and "
        f"word not in ({','.join('?' * len(exceptions))}) "
        "order by random() limit 1", exceptions
    )

def add_words(*words):
    with user_db.cursor() as c:
        for word, paraphrase in words:
            c.execute("update words set paraphrase = ? where word = ?", (paraphrase, word))
            c.execute("insert or ignore into words(word, paraphrase) values(?, ?)", (word, paraphrase))
