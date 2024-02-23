from datetime import datetime
import sys
import sqlite3
from urllib.parse import urlparse

cached_hosts = {}
new_hosts = {"cnt": 0}


def warm_cache(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, name from host")
    rows = cur.fetchall()
    for row in rows:
        cached_hosts[row[1]] = row[0]
    

def get_db(dbfile):
    conn = None
    try:
        conn = sqlite3.connect(dbfile)
    except Error as e:
        print(e)

    return conn


def get_unprocessed_hosts(conn, limit=5000):
    cur = conn.cursor()
    cur.execute("SELECT id, url from item where url is not null and host_id is null limit :limit", {'limit': limit})
    rows = cur.fetchall()
    return rows


def find_or_create_host(conn, host):
    id = cached_hosts.get(host, None)
    if not id:
        cur = conn.cursor()
        cur.execute("INSERT INTO host(name) VALUES (:name) RETURNING id", {'name': host})  
        rows = cur.fetchall()
        id = rows[0][0]
        cached_hosts[host] = id
        new_hosts["cnt"] += 1
    return id
#    cur = conn.cursor()
#    rows = cur.execute("SELECT id from host where name=:name", {'name': host}).fetchall()
#    if not rows:
#        cur.execute("INSERT INTO host(name) VALUES (:name) RETURNING id", {'name': host})  
#        rows = cur.fetchall()
#    return rows[0][0]    


def update_item(conn, id, url):
    host = urlparse(url).netloc
    host_id = find_or_create_host(conn, host)
    sql = "UPDATE item set host_id=:host_id WHERE id=:id"
    data = { 'host_id': host_id, 'id': id} 
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()


if __name__ == '__main__':
    dbfile = 'instance/hn.db'
    conn = get_db(dbfile)
    warm_cache(conn)
    print("start: " + str(datetime.now()))
    for i in range(0, 1000):
        rows =  get_unprocessed_hosts(conn)
        if len(rows) == 0:
            break;
        for row in rows:
            update_item(conn, row[0], row[1])
            
        print(str(i) + ": " + str(datetime.now()) + " " + str(new_hosts['cnt']) + " new host entries")
        new_hosts["cnt"] = 0
