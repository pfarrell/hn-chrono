import sys
import pandas as pd
import sqlite3

def dbimport(df, con, table):
    df = df.drop(columns=["timestamp", "ranking", "kids", "parts", "poll"], errors="ignore")
    df.to_sql(table, con, if_exists="append", index=False, chunksize=5000, method="multi")


if __name__ == '__main__':
    filepath = sys.argv[1]
    con = sqlite3.connect("hn.db")
    if filepath.endswith("parquet"):
        df = pd.read_parquet(filepath)
    elif filepath.endswith("json"):
        df = pd.read_json(filepath, lines=True)
    df['source'] = filepath
    dbimport(df, con, "items")
