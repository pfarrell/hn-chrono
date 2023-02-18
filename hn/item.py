from datetime import datetime, timezone, date, timedelta
import time
import math

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)

from hn.db import get_db

bp = Blueprint('item', __name__, url_prefix='/')

def curr_utc_time():
    return datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=timezone.utc).timestamp()


# Input unix epoch time, outputs date in YYYY-MM-DD format
def to_date(time):
    return datetime.utcfromtimestamp(int(time))    


def strdate(date):
    return date.strftime('%Y-%m-%d')


def time2strdate(time):
    return strdate(to_date(time))

bp.add_app_template_filter(to_date)
bp.add_app_template_filter(time2strdate)


records_size_cache={}

# Input unix epoch time, outputs tuple of yesterday and tomorrow in YYYY-MM-DD format
def surrounding_dates(time):
    dt = to_date(time)
    delta = timedelta(days=1)
    return (dt - delta, dt + delta)


def min_max_dates():
    db = get_db()
    sql="select date(min(time), 'unixepoch', 'localtime') from item UNION ALL select date(max(time), 'unixepoch', 'localtime') from item"
    rows=db.execute(sql).fetchall()
    return (rows[0][0], rows[1][0])


@bp.route('/', methods=(['GET']))
def items(limit=50, page=0):
    start_date = None
    if request.args.get('d'):
        start_date = request.args.get('d') + " +0000"
    if not start_date:
        start_time = request.args.get('t', curr_utc_time())
    else:
        start_time = datetime.strptime(start_date, '%Y-%m-%d %z').timestamp()
    if page == 0:
        page=request.args.get('p', 0)


    end_time = int(start_time)+86400
    offset = int(page) * limit
    data = {'limit': limit, 'start_time': start_time, 'end_time': end_time, 'offset': offset }

    db = get_db()
    total_records = records_size_cache.get(start_time)
    if not total_records:
        sql="""SELECT count(1) from item i join host h on h.id = i.host_id where i.type='story' 
                and dead is null and deleted is null and time between :start_time and :end_time"""
        print(sql)
        print(data)
        total_records = db.execute(sql, data).fetchall()[0][0]
        records_size_cache[start_time] = total_records
    pages = math.ceil(total_records/limit)

    sql="""select q.* from (SELECT i.id, i.type, i.score, i.by, i.title, i.url, i.text, i.time, i.parent, 
                        i.descendants, i.dead, i.deleted, i.rectified, i.source, h.name as host, i.captured_at 
                        from item i join host h on h.id = i.host_id where i.type='story' 
                        and dead is null and deleted is null
                        and time between :start_time and :end_time
                        order by time desc) q order by q.score desc limit :limit offset :offset"""
    print(sql)
    print(data)
    items=db.execute(sql, data).fetchall()
    print(f"{len(items)} records returned")
    prev, next = map(strdate, surrounding_dates(start_time))
    mindt, maxdt = min_max_dates()
    return render_template('items.html', items=items, title=strdate(to_date(start_time)), 
                           date=strdate(to_date(start_time)),next=next, prev=prev, mindt=mindt, 
                           maxdt=maxdt, pages=pages)


@bp.route('item/<id>', methods=(['GET']))
def item(id):
    db = get_db()
    sql="""WITH RECURSIVE discussion(id, type, score, by, title, url, text, time, parent, descendants, dead, 
                                    deleted, rectified, source, level, host) AS (
            select i.id, i.type, i.score, i.by, i.title, i.url, i.text, i.time, i.parent, i.descendants, i.dead, 
                    i.deleted, i.rectified, i.source, 0 as level, h.name as host 
            from item i 
            left join host h on h.id = i.host_id
            where i.id = :id 
            UNION ALL 
            SELECT  i.id, i.type, i.score, i.by, i.title, i.url, i.text, i.time, i.parent, i.descendants, i.dead, 
                    i.deleted, i.rectified, i.source, d.level+1 as level, NULL as host 
            from item i 
            join discussion d on d.id = i.parent 
            order by level DESC, i.score DESC) 
            select * from discussion"""
    print(sql)
    items=db.execute(sql, {'id': id}).fetchall()
    return render_template('items.html', items=items, title=items[0]['title'], date=strdate(to_date(items[0]['time'])),)


@bp.route('user/<by>', methods=(['GET']))
def user(by, limit=50, page=0):
    if page == 0:
        page=request.args.get('p', 0)
    db = get_db()
    total_records = records_size_cache.get(by)
    offset = int(page) * limit
    data = {'name': by, 'by': by, 'limit': limit, 'offset': offset}
    if not total_records:
        sql="""SELECT count(1) from item i left join host h on h.id = i.host_id where by=:by"""
        print(sql)
        print(data)
        total_records = db.execute(sql, data).fetchall()[0][0]
        records_size_cache[by] = total_records
    pages = math.ceil(total_records/limit)
    sql="""SELECT i.id, i.type, i.score, i.by, i.title, i.url, i.text, i.time, i.parent, i.descendants, 
                        i.dead, i.deleted, i.rectified, i.source, h.name, i.captured_at, i.user_id 
                        from item i left join host h on h.id = i.host_id where by=:by order by time desc limit :limit offset :offset"""
    print(sql)
    items=db.execute(sql, data).fetchall()
    sql="""SELECT id, name, created, karma, delay, about from user where name=:by"""
    user=db.execute(sql, data).fetchall()
    print(sql)
    return render_template('items.html', items=items, title=f"{by} posts", user=user[0], pages=pages)
