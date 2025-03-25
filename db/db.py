from yfinsuite.yfin_worker import *
import subprocess
import asyncio
import sqlite3


# Can use to import .yaml as a dict
# import yaml

# with open('config.yaml', 'r') as f:
#     config = yaml.safe_load(f) # returns dict

def db_connection():
    conn = sqlite3.connect("init.db")
    cursor = conn.cursor()
    return cursor, conn

cursor, conn = db_connection()


def create_db():
    with open('db/init.sql', 'r') as sql_file:
        create_table_query = sql_file.read()
    conn.execute(create_table_query)
    conn.commit()
    
    cursor.close()
    conn.close()


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
