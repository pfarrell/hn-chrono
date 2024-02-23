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


def get_min_id(conn, dt, mode):
    cur = conn.cursor()
    data = {'date': dt }
    if mode == 'unprocessed':
        sql = "SELECT id from item where time > :date and type='story' and rectified IS NULL order by time limit 1"
    elif mode == 'stories':
        sql = "SELECT id from item where time > :date and type='story' order by time limit 1"
    else:
        sql = "SELECT id from item where time > :date order by time limit 1"

    cur.execute(sql, data)
    rows = cur.fetchall()
    return rows[0][0]


def get_max_id(conn, dt, mode):
    cur = conn.cursor()
    data = {'date': dt }
    if mode != 'all':
        sql = "SELECT id from item where time < :date and type='story' and rectified IS NULL order by time desc limit 1"
    else:
        sql = "SELECT id from item where time < :date order by time desc limit 1"
    cur.execute(sql, data)
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


def upsert_item(conn, id, json, capture_time):
    sql = f"""INSERT INTO item(id, type, score, by, title, url, text, time, parent, descendants, dead, deleted) 
            VALUES(:id, :type, :score, :by, :title, :url, :text, :time, :parent, :descendants, :dead, :deleted)
            ON CONFLICT(id) DO UPDATE
            SET text=:text, descendants=:descendants, score=:score, title=:title, deleted=:deleted, 
            dead=:dead, url=:url, rectified=:rectified WHERE id=:id"""
    data = { 
            'by': json.get('by', None),
            'time': json.get('time', None),
            'type': json.get('type', None),
            'text': json.get('text', None), 
            'parent': json.get('parent', None),
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
    #for id in map(str.strip, sys.stdin):
    for id in range(37279413, 37284576):
        retrieval_time=int(time.time())
        fbdata = retrieve_from_firebase(id)
        upsert_item(conn, id, fbdata, retrieval_time)
        print(f"{datetime.now()}: updated id {id}"), 
