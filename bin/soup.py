import sys
import time
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import requests


def get_db(dbfile):
    conn = None
    try:
        conn = sqlite3.connect(dbfile)
    except Error as e:
        print(e)

    return conn


def retrieve_from_hn(id):
    ret={}
    resp = requests.get(f"https://news.ycombinator.com/item?id={id}", 
                    cookies={'user':"pfarrell&KcSvQvYc8bAZ3mPt3Dx0Nxt0zbhCQwsw"})
    soup = BeautifulSoup(resp.text, features="html.parser")

    if soup.select(".hnuser"):
        ret['by']=soup.select(".hnuser")[0].string
    else:
        return None
    ret['title']=soup.select("#pagespace")[0]["title"]
    ret['age']=parse_date(soup.select(".age")[0]['title']) # 2020-12-03T20:57:55 -> 1607029075 

    if soup.select(".score"):
        ret['score']=extract_int(soup.select(".score")[0].string) # "1 point" -> 1

    if soup.select(".titleline"):
        if soup.select(".titleline")[0].a:
            ret['url']=soup.select(".titleline")[0].a['href']

    if soup.select(".toptext"):
        ret['text']=soup.select(".toptext")[0].text

    if not ret.get('text'):
        if soup.select(".comment"):
            ret['text']=soup.select(".comment")[0].text

    return ret


def extract_int(str):
    return int(str.split(' ')[0])


def parse_date(str):
    dt = datetime.fromisoformat(str)
    return dt.replace(tzinfo=timezone.utc).timestamp()


def get_unknown_items(conn, limit=1000):
    cur = conn.cursor()
    sql="select id from item where user_id is null and dead is null and deleted is null limit :limit"
    cur.execute(sql, {'limit': limit})
    rows = cur.fetchall()
    return rows


def update_item(conn, dict, id):
    sql = "UPDATE item set by=:by, title=:title, text=:text, url=:url, time=:age, score=:score, rectified=:rectified where id=:id"
    data = {'id': id, 
            'by': get(dict, 'by'),
            'title': get(dict, 'title'), 
            'text': get(dict, 'text'),
            'url': get(dict, 'url'),
            'age': get(dict, 'age'),
            'score': get(dict, 'score'),
            'rectified': int(datetime.now().timestamp())
    }
    cur = conn.cursor()
    row = cur.execute(sql, data)
    conn.commit()


def get(dict, value, default=None):
    return dict.get(value, default)


if __name__ == '__main__':
    dbfile = 'instance/hn.db'
    conn = get_db(dbfile)
    print("start: " + str(datetime.now()))
    for i in range(0, 1000):
        ids = get_unknown_items(conn)
        if len(ids) == 0:
            sys.exit(0)
        for row in ids:
            id = row[0]
            time.sleep(.5)
            print(f"updating {id}")
            dict = retrieve_from_hn(id)
            if dict:
                update_item(conn, dict, id)
            else:
                print(f"item {id} not found in hn")
    print("complete: " + str(datetime.now()))
