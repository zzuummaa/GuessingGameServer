from os import path
import platform
import sqlite3

from flask import g

from tables import create_tables

if platform.system() == 'Linux':
    DATABASE = "/db/guessing_game.db"
elif platform.system() == "Windows":
    DATABASE = "guessing_game.db"


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE, isolation_level=None)
        # db.set_trace_callback(print)
        query_db("""PRAGMA foreign_keys = 1""")
        db.row_factory = make_dicts
    return db


def query_db(query, args=(), ret_lastrowid=False, ret_rowcount=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    if ret_lastrowid:
        return cur.lastrowid
    elif ret_rowcount:
        return cur.rowcount
    return rv


def create_db_if_not_exist():
    if not path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        create_tables(cursor)
        conn.commit()
        cursor.close()
        conn.close()
