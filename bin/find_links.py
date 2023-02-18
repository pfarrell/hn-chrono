import sys
import sqlite3
import re
from urllib.parse import urlparse



def get_db(dbfile):
    conn = None
    try:
        conn = sqlite3.connect(dbfile)
    except Error as e:
        print(e)

    return conn


def get_items(conn, id, limit=5000):
    cur = conn.cursor()
    sql = "SELECT id, by, text from item i where text is not null and id > :id order by id limit :limit"
    cur.execute(sql, {'id': id, 'limit':limit});
    rows = cur.fetchall()
    return rows


def extract_links(str):
    REGEX=r"(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"
    links = re.findall(REGEX, str)
    return links



if __name__ == '__main__':
    start_id=sys.argv[0]
    dbfile = 'instance/hn.db'
    conn = get_db(dbfile)
    last_id=0
    for i in range(0,10**6):
        items = get_items(conn, last_id)
        if not items:
            sys.exit(0)
        for item in items:
            id, by, text = item
            last_id = id
            links = extract_links(text)
            if(links):
                print(f"{id}, {by}, {links}")

