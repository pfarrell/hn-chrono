#!/usr/bin/env bash
set x

rm -f missing.json
# Get latest id from db
dbid=$(sqlite3 hn.db "select max(id) from items")
# Get latest id from firebase
fbid=$(curl -s https://hacker-news.firebaseio.com/v0/maxitem.json)

# loop over missing ids
echo "latest dbid: $dbid, latest firebaseid: $fbid" 
dbid=$((dbid+1))
for id in $(seq $dbid $fbid); do 
  if [ $(expr $id % 100) == "0" ]; then
        echo "$id"
  fi
  curl -s https://hacker-news.firebaseio.com/v0/item/$id.json >> missing.json
  echo >> missing.json
done
echo "importing $(<missing.json wc -l) records into db"
python ./bin/import.py missing.json
#rm -f missing.json
