SQLs = {}

SQLs['0.1'] = """
create table words (
    id integer primary key autoincrement,
    word varchar(128) not null unique,
    paraphrase text not null default '',
    show_paraphrase bool not null default 0,
    color varchar(32) not null default 'white',
    cleared bool not null default 0
);
create unique index index_word on words(word);
"""
