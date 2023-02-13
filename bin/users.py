from datetime import datetime
import sys
import sqlite3
from urllib.parse import urlparse

cached_hosts = {}


def get_db(dbfile):
    conn = None
    try:
        conn = sqlite3.connect(dbfile)
    except Error as e:
        print(e)

    return conn


def get_unknown_users(conn, limit=5000):
    cur = conn.cursor()
    cur.execute("SELECT distinct by from item i where by is not null and not exists (SELECT name from user u where i.by = u.name) limit :limit", {'limit': limit});
    rows = cur.fetchall()
    return rows


def create_user(conn, username):
    sql = "INSERT INTO user(name) VALUES(:username) RETURNING id"
    cur = conn.cursor()
    cur.execute(sql, {'username': username})
    row = cur.fetchall()
    return row[0][0]


def update_items(conn, username, id):
    sql = "UPDATE item set user_id = :userid where by=:username"
    data = {'userid': id, 'username': username}
    cur = conn.cursor()
    row = cur.execute(sql, data)
    conn.commit()


if __name__ == '__main__':
    dbfile = 'instance/hn.db'
    conn = get_db(dbfile)
    print("start: " + str(datetime.now()))
    for i in range(0, 1000):
        users = get_unknown_users(conn)
        if len(users) == 0:
            break;
        for user in users:
            id = create_user(conn, user[0])
            update_items(conn, user[0], id)

        print(str(i) + ": " + str(datetime.now()))
