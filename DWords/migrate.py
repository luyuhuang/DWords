SQLs = {}

SQLs['0.1'] = """
create table words (
    id integer primary key autoincrement,
    word varchar(128) not null unique,
    paraphrase text not null default '',
    show_paraphrase bool,
    color varchar(32),
    cleared bool not null default 0
);
create unique index index_word on words(word);

create table setting (
    key varchar(128) primary key,
    value text not null default 'None'
);
"""
