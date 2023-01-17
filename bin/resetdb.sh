#!/usr/bin/env bash

data_file=hn-stories.csv
db_name=hn.db

sqlite3 $db_name 'CREATE TABLE IF NOT EXISTS "items"("id" INTEGER, "type" TEXT, "score" INTEGER, "by" TEXT, "title" TEXT, "url" TEXT, "text" TEXT, "time" INTEGER, "parent" INTEGER, "descendants" INTEGER, "dead" INTEGER, "deleted" INTEGER, "rectified" TEXT, "source" TEXT)'
sqlite3 $db_name 'CREATE UNIQUE INDEX IF NOT EXISTS items_ids on items(id)'
sqlite3 $db_name 'CREATE INDEX IF NOT EXISTS items_types on items(type)'
sqlite3 $db_name 'CREATE INDEX IF NOT EXISTS items_time on items(time, id)'
#sqlite3 $db_name 'VACUUM'
