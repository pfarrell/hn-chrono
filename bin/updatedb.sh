#!/usr/bin/env bash
set x

rm -f missing.json
dbfile="instance/hn.db"
# Get latest id from db
dbid=$(sqlite3 $dbfile "select max(id) from item")
# Get latest id from firebase
fbid=$(curl -s https://hacker-news.firebaseio.com/v0/maxitem.json)

date=$(date '+%Y%m%d_%H%m%S')

# loop over missing ids
echo "latest dbid: $dbid, latest firebaseid: $fbid" 
dbid=$((dbid+1))
for id in $(seq $dbid $fbid); do 
  if [ $(expr $id % 100) == "0" ]; then
        echo "$id"
  fi

  result=$(curl -s https://hacker-news.firebaseio.com/v0/item/$id.json)
  if [ "$result" != "null" ]; then
    echo "$result" >> $date.json
    echo >> $date.json
  fi
done
echo "importing $(<$date.json wc -l) records into db"
python ./bin/import.py $date.json $dbfile
mv $date.json hn_raw/
