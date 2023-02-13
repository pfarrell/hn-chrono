CREATE TABLE IF NOT EXISTS item(
  id INTEGER, 
  type TEXT, 
  score INTEGER, 
  by TEXT, 
  title TEXT, 
  url TEXT, 
  text TEXT, 
  time INTEGER, 
  parent INTEGER, 
  descendants INTEGER, 
  dead INTEGER, 
  deleted INTEGER, 
  rectified TEXT, 
  source TEXT,
  host_id INTEGER,
  captured_at INTEGER NOT NULL DEFAULT (UNIXEPOCH())
, user_id INTEGER);
CREATE TABLE IF NOT EXISTS host(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS user(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT,
  created INTEGER,
  karma INTEGER,
  delay INTEGER,
  about TEXT
);




CREATE UNIQUE INDEX IF NOT EXISTS item_ids on item(id);

CREATE INDEX IF NOT EXISTS item_times on item(time, type, id);

CREATE INDEX IF NOT EXISTS host_names on host(name, id);

CREATE INDEX IF NOT EXISTS item_hosts on item(host_id, id);

CREATE INDEX IF NOT EXISTS user_names on user(name, id);

CREATE INDEX IF NOT EXISTS item_bys on item(by, id);

CREATE INDEX IF NOT EXISTS host_user_ids on item(user_id, host_id, id, time);

CREATE INDEX IF NOT EXISTS item_parent_ids on item(parent, id, time);
