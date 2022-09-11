import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

queryStr = """
MATCH (p:Site),(q:Site)
WHERE p.title = q.title AND id(p) < id(q)
WITH p,q LIMIT 1
MATCH (r:Site)
WHERE p.title = r.title
WITH count(r) AS cnt, [p]+collect(r) AS rs, r.title AS title
CALL apoc.refactor.mergeNodes(rs) YIELD node
RETURN cnt, title
"""

load_dotenv()
url = os.environ.get('NEO4J_SERVER_URL')
username = os.environ.get('NEO4J_USERNAME')
password = os.environ.get('NEO4J_PASSWORD')
conn = GraphDatabase.driver(
            url,
            auth=(
                username,
                password
            )
        )
conn.verify_connectivity()
with conn.session() as session:
    while True:
        res = session.run(queryStr)
        a = [x for x in res]
        print(a)
        if(len(a) == 0):
            break
conn.close()