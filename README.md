# Hacker News Data

These notes are my personal observations on assembling a dataset for this content.  Since I'm not affiliated with YCombinator, Microsoft, or Google, I'm not warranting this the most efficient way, but it works for me and my purposes.

We _could_ scrape the actual website, but with close to 39.8 records (as of March 2024), at 10 records per second, we're looking at 45 days to get the full data set.

Some research I did shows there is a backup on Micrsoft's BigQuery and there is a Firebase database that is updated in near real time.  We can use the BigQuery data to download a historical chunk and then get more recent data from Firebase. 

### Schema

|column|data type| notes|
|---|---|---|
|id|int|numeric id for the submission|
|type|string|item type, one of story, comment, job, poll, pollopt|
|score|int|story points, comment points are not publicly avaialble|
|by|string|username of submitter|
|title|string|title of submission, null if type is not story|
|url|string|link for stories, null if type is not story|
|text|string|comment text, generally null if type is story|
|time|int|unix epoch time of publishing|
|parent|int|parent item.  null if type is story|
|descendants|int|number of item descedants|

### Data Locations

#### The Archive
You can find an historical archive of hacker news hosted on [Google's BigQuery](https://console.cloud.google.com/bigquery?p=bigquery-public-data&d=hacker_news).  Unfortunately, the data stopped being updated `2022-11-16 09:12:32 UTC`.  We'll call that our data epoch.  Everything in that set is fixed and assumed to be good.

<img alt="good and cheap but not fast" src="img/good_and_cheap.png" style="float: right">

#### Hacker News API (Firebase)
Firebase provides some client libraries that can capture changes as near real time events.  The design of this project is to build a dataset, not mirror the data in real time, so we'll go for a more quick and dirty daily download of new data (i.e. items we haven't seen before) and we can upsert stories and comments that are older than a few days so we get the "final" story scores and comment edits.  _Final_ because technically points can change over time, but rarely change after a few days from post. 

#### Building our dataset

* Download the BigQuery data
* Download item data from Firebase from data epoch to present
* Merge data into a database
* [Scripts](https://github.com/pfarrell/hn-chrono/tree/main/bin) to upsert database with latest data 

#### Publishing the dataset

I had a great idea to publish the files as a git repository on github, but this doesn't seem feasible.  Even compressed, the dataset is around 5 gigs of data.  This is outside the bounds of what a git repository should handle, likewise, I expect to automatically publish new data every day, so each commit will add a bunch of object data to the repository so it can constuct diffs of commits.  I _could_ use git-lfs, but then I have to host the files somewhere, other users will have to use git-lfs, and they won't be able to download portions of the dataset... it would be all or nothing.  Instead of going through that much trouble, I'll host a webpage with the latest download links on both my website and on github, store the files in my home setup, and call it a day.

Find the links to the data at the [hn-chrono github](https://github.com/pfarrell/hn-chrono) or at [patf.com/hn-data](https://patf.com/hn-data/).

If this ever gets some attention, we change this whole process to a torrent.
