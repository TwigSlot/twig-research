from curses import meta
import scrapy

class WikiSpider(scrapy.Spider):
    name = 'wiki'
    start_urls = ['https://en.wikipedia.org/wiki/Quantum_field_theory']
    allowed_domains = ["en.wikipedia.org"]

    custom_settings = {
        'DEPTH_LIMIT': 10,
        'DEPTH_PRIORITY': 1
    }

    def __init__(self):
        self.state = {}

    def parse(self, response):
        title = response.css('span.mw-page-title-main::text').get()
        if(title is None):
            title = response.css('h1.firstHeading::text').get()
        if(title):
            yield {
                'title': title,
                'url': response.url,
                'from': response.meta.get('from')
            }
        else:
            return
        yield from  response.follow_all(
                        css='a::attr(href)', 
                        callback=self.parse, 
                        meta = {
                            'from': response.url
                        }
                    )