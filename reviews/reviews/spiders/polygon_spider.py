import scrapy


class QuotesSpider(scrapy.Spider):
    name = "polygon"

    def start_requests(self):
        urls = [
            'http://polygon.com/games/reviewed'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # follow pagination links
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)