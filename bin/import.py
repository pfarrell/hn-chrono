import sys
import pandas as pd
import sqlite3

def dbimport(df, con, table):
    df = df.drop(columns=["timestamp", "ranking", "kids", "parts", "poll"], errors="ignore")
    # rectify some items now being published with a list for deleted instead of a boolean
#    df['deleted'] = df['deleted'].apply(lambda x: x if isinstance(x, bool) else bool(x))
    df.to_sql(table, con, if_exists="append", index=False, chunksize=1, method="multi")


if __name__ == '__main__':
    filepath = sys.argv[1]
    dbpath = sys.argv[2]
    con = sqlite3.connect(dbpath)
    if filepath.endswith("parquet"):
        df = pd.read_parquet(filepath)
    elif filepath.endswith("json"):
        df = pd.read_json(filepath, lines=True)
    df['source'] = filepath
    dbimport(df, con, "item")
