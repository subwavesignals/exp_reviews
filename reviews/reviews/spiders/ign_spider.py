import scrapy


class QuotesSpider(scrapy.Spider):
    name = "ign"

    def start_requests(self):
        urls = ['http://ign.com/games/reviews']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # follow pagination links
        num_pages = 1
        next_page = response.css('a.is-more-reviews::attr(href)').extract_first()
        print next_page
        if next_page is not None and num_pages <= 10:
            num_pages += 1
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_reviews)

    def parse_reviews(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        yield {
            'name': extract_with_css('div.item_title h3 a::text'),
            'score': extract_with_css('div.scorebox span.scoreBox-score::text'),
        }