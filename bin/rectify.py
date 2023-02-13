import sys
import sqlite3
import requests
import json
import time
from datetime import datetime, timedelta


def get_db(dbfile):
    conn = None
    try:
        conn = sqlite3.connect(dbfile)
    except Error as e:
        print(e)

    return conn


def get_dates(datestr):
    dt = datetime.strptime(datestr + " +0000", '%Y-%m-%d %z')
    maxDt = dt + timedelta(days=1)
    return dt.timestamp(), maxDt.timestamp()


def get_min_id(conn, dt):
    cur = conn.cursor()
    cur.execute(f"SELECT id from item where time > :date and type='story' and rectified IS NULL order by time limit 1", {'date': dt})
    rows = cur.fetchall()
    return rows[0][0]


def get_max_id(conn, dt):
    cur = conn.cursor()
    cur.execute(f"SELECT id from item where time < :date and type='story' and rectified is NULL  order by time desc limit 1", {'date': dt})
    rows = cur.fetchall()
    return rows[0][0]

def retrieve_from_firebase(id):
    url = f"https://hacker-news.firebaseio.com/v0/item/{id}.json"
    return json.loads(requests.get(url).text)


def retrieve_from_db(conn, id):
    cur = conn.cursor()
    cur.execute(f"SELECT * from item where id = :id", {'id': id})
    return cur.fetchall()[0]


def is_story(conn, id):
    cur = conn.cursor()
    cur.execute(f"SELECT count(1) from item where id = :id and type='story'", {'id': id})
    return cur.fetchone()[0] == 1


def update_item(conn, id, json, capture_time):
    sql = f"""UPDATE item 
            set text=:text, descendants=:descendants, score=:score, title=:title, deleted=:deleted, 
            dead=:dead, url=:url, rectified=:rectified WHERE id=:id"""
    data = { 
            'text': json.get('text', None), 
            'descendants': json.get('descendants', None), 
            'score': json.get('score', None), 
            'title': json.get('title', None), 
            'deleted': json.get('deleted', None), 
            'dead': json.get('dead', None), 
            'url': json.get('url', None),
            'rectified': capture_time,
            'id': json['id']
        } 
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()


if __name__ == '__main__':
    dbfile = 'instance/hn.db'
    conn = get_db(dbfile)
    minDate, maxDate = get_dates(sys.argv[1])
    minId = get_min_id(conn, minDate)
    maxId = get_max_id(conn, maxDate)
    updates = maxId - minId
    print(f"{datetime.now()}: updating {updates} records")
    for id in range(minId, maxId):
        retrieval_time=int(time.time())
        if is_story(conn, id):
            fbdata = retrieve_from_firebase(id)
            update_item(conn, id, fbdata, retrieval_time)
            if (id - minId) % 250 == 0:
                print(f"{datetime.now()}: updated id {id}, {id - minId} of {updates}"), 
