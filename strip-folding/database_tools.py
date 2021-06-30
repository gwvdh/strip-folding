import sqlite3
from sqlitedict import SqliteDict


DICT_DATABASE_PATH: str = 'output/dict_database_2.db'
DATABASE_PATH: str = 'output/database_3.db'


def open_database():
    """
    Open the database and return the connection and cursor of the SQLite database
    :return:
    """
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS strips
                   (strip_name text, 
                   len INTEGER, 
                   n_creases INTEGER, 
                   M_creases INTEGER, 
                   creases INTEGER, 
                   crease_direction INTEGER,
                   layers text)'''
                )
    return con, cur


def insert_data(data, cursor):
    """
    Insert the given data into the SQLite database.

    :param data: tuple of data
    :param cursor: cursor of the SQLite database
    :return:
    """
    sql = 'INSERT INTO strips(strip_name, len, n_creases, M_creases, creases, crease_direction, layers) ' \
          'VALUES(?, ?, ?, ?, ?, ?, ?)'
    cursor.execute(sql, data)


def open_dict_database():
    return SqliteDict(DICT_DATABASE_PATH, autocommit=True)


def merge_databases(new_database):
    old_database = open_dict_database()
    for strip, order_data in new_database.items():
        if strip in old_database:
            for order, data in order_data.items():
                if order not in old_database[strip]:
                    old_database[strip][order] = data
        else:
            old_database[strip] = order_data
