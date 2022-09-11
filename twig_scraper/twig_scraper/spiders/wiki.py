import scrapy
from scrapy.http.response import Response, Request
from dotenv import load_dotenv
import os
from neo4j import GraphDatabase, Neo4jDriver
from scrapy.linkextractors import LinkExtractor

class WikiSpider(scrapy.Spider):
    name = 'wiki'
    start_urls = ['https://en.wikipedia.org/wiki/Quantum_field_theory']
    allowed_domains = ["en.wikipedia.org"]
    le = LinkExtractor()

    custom_settings = {
        'DEPTH_LIMIT': 10,
        'DEPTH_PRIORITY': 1
    }

    def __init__(self):
        self.state = {}
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

    def parse(self, response):
        title = response.css('span.mw-page-title-main::text').get()
        if(title is None):
            title = response.css('h1.firstHeading::text').get()
        for link in self.le.extract_links(response):
            url = link.url
            item = {
                'title': title, # current title
                'from': response.url, # from current
                'url': url # to new
            }
            yield item

            with self.conn.session() as session:
                # create node
                queryStr = f"MERGE (n:Site {{ url: $url, title: $title }})" 
                session.run(queryStr, {'title': item['title'], 'url': item['from']})
                # create edge
                queryStr = f"MATCH (a:Site),(b:Site)\
                        WHERE a.url = $from_url AND b.url = $to_url\
                            MERGE (a)-[e:Reference]->(b)"
                session.run(queryStr, {'from_url': item['from'], 'to_url': item['url']})
 
            yield response.follow(
                        url = url,
                        callback = self.parse, 
                    )
    
    def close_spider(self):
        self.conn.close()