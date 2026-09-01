#! /usr/bin/env bash
#

db_location='instance/hn.db' 
sshcmd=ssh
scpcmd=scp

exportData() {
  local y=$1
  local m=$2
  local sql="SELECT id,type,score,by,title,url,text,time,parent,descendants,dead,deleted from item where strftime('%Y-%m', time, 'unixepoch')=\"$y-$m\""
  echo "exporting from db for $y-$m"
  sqlite3 $db_location -csv -header "$sql" > $y-$m.csv
  rm $y-$m.csv.gz
  echo "zipping db output"
  gzip -9 $y-$m.csv
  echo "creating year directory for $y"
  $sshcmd pfarrell@172.16.1.15 "mkdir /volume1/hn-data/$y"
  echo "copying file to synology: $y-$m.csv.gz"
  $scpcmd $y-$m.csv.gz pfarrell@172.16.1.15:/hn-data/$y/
  rm $y-$m.csv.gz
}  


year=$(date +%Y)
month=$(date +%m)
lastmonth=$(date -d "$(date +%Y-%m-1) -1 month" +%m)
day=$(date +%d)

if [ -z "$SSH_AUTH_SOCK" ]
then
    export SSH_AUTH_SOCK=/run/user/1000/keyring/ssh
fi

if [ -e $year-$month.csv.gz ]
then
  rm $year-$month.csv.gz
fi

exportData $year $month

if (($day <= 22)) 
then
  exportData $year $lastmonth
fi

echo "generating file report"
python ./bin/generate_file_report.py

echo "adding to git repo"
git add fileinfo.html
echo "committing to git repo"
git commit -m "updated $(date +%Y-%m-%d) export"
echo "pushing to remote git repo"

git push
echo "copying file to webserver"
$scpcmd fileinfo.html pfarrell@172.16.1.15:/hn-data/index.html
