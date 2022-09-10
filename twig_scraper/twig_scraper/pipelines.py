# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
from neo4j import GraphDatabase, Neo4jDriver
from dotenv import load_dotenv

class TwigScraperPipeline:
    def __init__(self):
        load_dotenv()
        self.url = os.environ.get('NEO4J_SERVER_URL')
        self.username = os.environ.get('NEO4J_USERNAME')
        self.password = os.environ.get('NEO4J_PASSWORD')
        print(f"connecting to neo4j {self.url}")
        self.conn = GraphDatabase.driver(
            self.url,
            auth=(
                self.username,
                self.password
            )
        )
        self.conn.verify_connectivity()
        print("verified neo4j connection")
    def process_item(self, item, spider):
        with self.conn.session() as session:
            queryStr = f"MERGE (n:Site {{ url: $url, title: $title }})"
            session.run(queryStr, {'title': item['title'], 'url': item['url']})
            if(item['from']):
                queryStr = f"MATCH (a:Site),(b:Site)\
                        WHERE a.url = $from_url AND b.url = $to_url\
                            MERGE (a)-[e:Reference]->(b)"
                session.run(queryStr, {'from_url': item['from'], 'to_url': item['url']})
        return item
    def close_spider(self, spider):
        self.conn.close()
