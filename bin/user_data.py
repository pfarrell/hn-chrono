from datetime import datetime
import sys
import sqlite3
import json
import requests
from urllib.parse import urlparse

cached_hosts = {}


def get_db(dbfile):
    conn = None
    try:
        conn = sqlite3.connect(dbfile)
    except Error as e:
        print(e)

    return conn


def retrieve_from_firebase(userid):
    url = f"https://hacker-news.firebaseio.com/v0/user/{userid}.json"
    return json.loads(requests.get(url).text)


def get_unknown_users(conn, limit=5000):
    cur = conn.cursor()
    cur.execute("SELECT id, name from user where karma is null limit :limit", {'limit': limit});
    rows = cur.fetchall()
    return rows


def get(dict, value, default=None):
    return dict.get(value, default)

def update_user(conn, dict, id):
    sql = "UPDATE user set created=:created, about=:about, karma=:karma, delay=:delay where id=:id"
    data = {'id': id, 
            'created': get(dict, 'created'), 
            'about': get(dict, 'about'),
            'karma': get(dict, 'karma'),
            'delay': get(dict, 'delay')
    }
    cur = conn.cursor()
    row = cur.execute(sql, data)
    conn.commit()


if __name__ == '__main__':
    dbfile = 'instance/hn.db'
    conn = get_db(dbfile)
    print("start: " + str(datetime.now()))
    users = get_unknown_users(conn)
    if len(users) == 0:
        sys.exit(0)
    for user in users:
        dict = retrieve_from_firebase(user[1])
        if dict:
            update_user(conn, dict, user[0])
        else:
            print(f"user {user[1]} not found in firebase")
