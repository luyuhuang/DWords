SQLs = {}

SQLs['0.1.0'] = """
create table words (
    word varchar(128) primary key,
    time integer not null default
        (cast((julianday('now') - 2440587.5) * 86400000 as integer)),
    modify_time integer not null default
        (cast((julianday('now') - 2440587.5) * 86400000 as integer)),
    paraphrase text not null default '',
    show_paraphrase bool,
    color varchar(32),
    cleared bool not null default 0
);

create table setting (
    key varchar(128) primary key,
    value text not null default 'None'
);

create table sync_cache (
    word varchar(128) primary key,
    op varchar(8),
    time integer
);
"""
