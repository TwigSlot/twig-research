import scrapy

class WikiSpider(scrapy.Spider):
    name = 'wiki'
    start_urls = ['https://en.wikipedia.org/wiki/Quantum_field_theory']
    allowed_domains = ["en.wikipedia.org"]

    def __init__(self):
        self.state = {}

    def parse(self, response):
        title = response.css('span.mw-page-title-main::text').get()
        if(title is None):
            title = response.css('h1.firstHeading::text').get()
        if(title):
            yield {
                'title': title,
                'url': response.url
            }
        else:
            return
        if('count' in self.state):
            self.state['count'] += 1
        else:
            self.state['count'] = 1
        if(self.state['count'] > 10):
            return
        yield from response.follow_all(css='a::attr(href)', callback=self.parse)