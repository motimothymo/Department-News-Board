USE DNB;

CREATE TABLE IF NOT EXISTS files
(
    id       int auto_increment
        primary key,
    news_id  int          not null,
    filename varchar(200) not null,
    filepath varchar(300) not null,
    constraint files_filepath_uindex
        unique (filepath),
    constraint files_id_uindex
        unique (id)
);

CREATE TABLE IF NOT EXISTS news
(
    id        int auto_increment
        primary key,
    title     text                 not null,
    content   text                 not null,
    datetime  datetime             not null,
    publisher varchar(50)          not null,
);

CREATE TABLE IF NOT EXISTS users
(
    username varchar(50)  not null
        primary key,
    password varchar(100) not null,
    constraint user_username_uindex
        unique (username)
);