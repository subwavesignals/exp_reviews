import scrapy


class QuotesSpider(scrapy.Spider):
    name = "gamespot"

    def start_requests(self):
        urls = [
            'http://gamespot.com/reviews'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # follow pagination links
        num_pages = 1
        next_page = response.css('li.paginate__item.skip.next::attr(href)').extract_first()
        print next_page
        if next_page is not None and num_pages <= 10:
            num_pages += 1
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse_reviews)

    def parse_reviews(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        yield {
            'name': extract_with_css('li.promo-strip__item div.media_body h3::text'),
            'score': extract_with_css('div.gs-score__inner div.gs_score__cell::text'),
        }