import random
import sqlalchemy, yaml
from sqlalchemy import text


with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

table = 'apartments'

url = config['database']['url']
engine = sqlalchemy.create_engine(url)
sites = ['compass', 'redfin', 'zillow', 'streeteasy']
with engine.connect() as conn:
            # q = '''select * from apartments where site = '{}' '''.format(j)
            #     result = conn.execute(text(q))
            # results = [f'{x} | ' for x in result]
            
            # results = ['site.com', 'site2.com']
            
            # for r in results:
            #     id_ = str(random.randint(0, 500000000)) # idc
            #     tup = (id_, j, r)

            #     q = '''
            #     INSERT INTO apartments (id, site, link)
            #     VALUES ({}, '{}', '{}');
            #     '''.format(*tup)
            #     result = conn.execute(text(q))
            #     conn.commit()
            #     print(f"Inserted {tup} to apartment table")


    q = '''select * from apartments'''
    result = conn.execute(text(q))
    print(f"all apartments: {[x for x in result]}")
