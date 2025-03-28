import sys, os
sys.path.append(os.path.abspath("C:/Users/charl/Documents/biz-scripts/yfinsuite"))
import subprocess
import asyncio
import json
import sqlite3
python_path = "C:/Users/charl/Documents/biz-scripts/biz-env/Scripts/python.exe"

# Can use to import .yaml as a dict
# import yaml

# with open('config.yaml', 'r') as f:
#     config = yaml.safe_load(f) # returns dict




def db_connection():
    conn = sqlite3.connect("stocks.db")
    cursor = conn.cursor()
    return cursor, conn
cursor, conn = db_connection()



def create_db():
    with open('db/sql/init.sql', 'r') as sql_file:
        create_table_query = sql_file.read()
    conn.execute(create_table_query)
    conn.commit()

def insert_row_to_db(row:json) -> int:
    try:
        with open('db/sql/insert_row.sql', 'r') as sql_file:
            query = sql_file.read()
        cursor.execute(query, {'json': row})
    except Exception as e:
        breakpoint()
        print(f"failed to insert {row['displayName']}\texception: {e}")
        return 1
    return 0

if __name__ == '__main__':
    # Querying the db returns a Row object

    runfrom = r"C:/Users/charl/Documents/biz-scripts"
    create_db()
    command = f"{python_path} {runfrom}/yfinsuite/yfin_worker.py -t tsla -f --to_json"
    data = json.loads(subprocess.run(command, capture_output=True).stdout)
    insert_row_to_db(data)
    breakpoint()

# gameplan:
    # We need to amass a dataset concurrently. We can use async to run the yfin_worker.py at maybe 10-20 threads at a time.
    # Each thread will hit the yfin endpoint to grab stats. We can store each thread's output as a pd.Series, merging to a DF.
    # Not entirely sure which sectors/tickers the dataset will be composed of (TBD). Also reaaallly want to include historical data.
    # Once this final df is composed, we can do some DSA on it -- graphing, dimensionality reduction, variance, clustering --
    # then finally do some cosine similarity/KNN/some hybrid collaborative filtering to find the nearest neighbor. We can
    # also maybe try and predict a data point from its stats? That can be a v2.

# Questions
    # How many threads can I run in parallel? 20/50 re: GPT
    # Is a DF the best way to store this data? We need to be mindful of the resources used whilst creating/amassing this DF.
        # We could also just write to a db. Postgres is free... YES DO THIS
    # Can we incorporate some sort of sharding/caching in case the DF balloons and we run out of memory? Is this overengineering?
        # Yes -- 
    # Is there a sexier algo than CF to deliver comparisons to a ticker?
