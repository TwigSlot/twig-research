import scrapy

class WikiSpider(scrapy.Spider):
    name = 'wiki'
    start_urls = ['https://en.wikipedia.org/wiki/Quantum_field_theory']

    def __init__(self):
        self.state = {}

    def parse(self, response):
        yield {
            'title': response.css('span.mw-page-title-main::text').get(),
            'url': response.url
        }
        if('count' in self.state):
            self.state['count'] += 1
        else:
            self.state['count'] = 1
        if(self.state['count'] > 10):
            return
        yield from response.follow_all(css='a::attr(href)', callback=self.parse)