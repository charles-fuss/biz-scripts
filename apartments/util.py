from openai import OpenAI
import yaml
import pandas as pd
import random
import sqlalchemy, yaml
from sqlalchemy import text
from io import StringIO
from typing import Union

with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

table = 'apartments'

def db_pipeline() -> Union[pd.DataFrame | str]:
    url = config['database']['url']
    engine = sqlalchemy.create_engine(url)
    with engine.connect() as conn:
        with open(f"queries/query.txt", 'r', encoding='utf-8') as f: query = f.read()
        q = '''select distinct link from apartments'''
        exclude = conn.execute(text(q))
        exclude = [f'{x} | ' for x in exclude]
        print(f"Excluding {exclude}")
        query += f'\nUNDER NO CIRCUMSTANCES SHOULD YOU INCLUDE ANY OF THESE APARTMENTS, THEY ARE DUPLICATES: {exclude}'
        
        print(f"Querying ChatGPT")
        results = openai_query(query)

        try: 
            csv_data = StringIO(results)
            df = pd.read_csv(csv_data)
        except: 
            print(f"ChatGPT probably returned a non-csv result: ({results})")
            return results

        for _, row in df.iterrows():
            link = row['Link']
            id_ = str(random.randint(0, 500000000)) # idc
            tup = (id_, 'all', link)
            q = '''
            INSERT INTO apartments (id, site, link)
            VALUES ({}, '{}', '{}');
            '''.format(*tup)
            _ = conn.execute(text(q))
            conn.commit()
            print(f"Inserted {tup} to apartment table")
        return results


def openai_query(query):
    client = OpenAI(api_key=config['oai_api_key'])

    resp = client.responses.create(
        model="gpt-5",         
        input=query,
        reasoning={ "effort": "high" },
        text={ "verbosity": "low" },
        tools=[{"type": "web_search"}]

    )
    return resp.output_text