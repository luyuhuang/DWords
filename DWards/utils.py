from db import user_db

def clear_words(*words):
    with user_db.cursor() as c:
        c.execute(f"update words set cleared = true where word in ({','.join('?' * len(words))})", words)

def redo_words(*words):
    with user_db.cursor() as c:
        c.execute(f"update words set cleared = false where word in ({','.join('?' * len(words))})", words)

def delete_words(*words):
    with user_db.cursor() as c:
        c.execute(f"delete from words where word in ({','.join('?' * len(words))})", words)

def random_one_word(*exceptions):
    return user_db.getOne("select word, paraphrase, show_paraphrase, color "
        "from words where cleared = false and "
        f"word not in ({','.join('?' * len(exceptions))}) "
        "order by random() limit 1", exceptions
    )
