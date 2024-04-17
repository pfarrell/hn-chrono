import sys
import sqlite3
import re
from urllib.parse import urlparse
from html import unescape



def get_db(dbfile):
    conn = None
    try:
        conn = sqlite3.connect(dbfile)
    except Error as e:
        print(e)

    return conn


def get_items(conn, id, limit=5000):
    #print(f"get_items from: {id}")
    cur = conn.cursor()
    sql = "SELECT id, by, text, type, url from item i where id > :id order by id limit :limit"
    cur.execute(sql, {'id': id, 'limit':limit});
    rows = cur.fetchall()
    return rows


def extract_links(str):
    text = unescape(str)
    
    # Regular expression pattern to match HTTP links
    pattern = re.compile(r'https?://\S+')
    
    # Find all matches in the text
    links = re.findall(pattern, text)
    
    return links




if __name__ == '__main__':
    dbfile = 'instance/hn.db'
    conn = get_db(dbfile)
    last_id=0
    for i in range(0,10**6):
        items = get_items(conn, last_id)
        if not items:
            sys.exit(0)
        for item in items:
            links=[]
            id, by, text, type, url = item
            last_id = id
            if(text):
                links = extract_links(text)
            if(url):
                links.append(url)
            if(links):
                print(f"{id}, {by}, {type}, {links}")

