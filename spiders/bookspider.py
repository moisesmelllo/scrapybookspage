import scrapy
from bookscraper.items import BookscraperItem
from random import randint
API_KEY = ''

class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        'FEEDS': {
            'booksdata.json': {'format': 'json', 'overwrite': True},
        }
    }

    def parse(self, response, **kwargs):
        books = response.xpath("//article[@class='product_pod']")

        for book in books:

            relative_url = book.xpath(".//h3//a//@href").get()

            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            yield response.follow(book_url, callback=self.parse_book_page)

        next_page = response.xpath("//li[@class='next']//@href").get()

        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_page(self, response, **kwargs):

        book_item = BookscraperItem()
        table_rows = response.xpath("//table//tr")

        book_item['url'] = response.url,
        book_item['title'] = response.xpath(".//div//h1/text()").get(),
        book_item['upc'] = table_rows[0].xpath(".//td/text()").get(),
        book_item['product_type'] = table_rows[1].xpath(".//td/text()").get(),
        book_item['price_excl_tax'] = table_rows[2].xpath(".//td/text()").get(),
        book_item['price_incl_tax'] = table_rows[3].xpath(".//td/text()").get(),
        book_item['tax'] = table_rows[4].xpath(".//td/text()").get(),
        book_item['availability'] = table_rows[5].xpath(".//td/text()").get(),
        book_item['num_reviews'] = table_rows[6].xpath(".//td/text()").get(),
        book_item['stars'] = response.xpath('//*[@id="content_inner"]/article/div[1]/div[2]/p[3]/@class').get(),
        book_item['category'] = response.xpath(".//ul[@class='breadcrumb']/li["
                                               "@class='active']/preceding-sibling::li["
                                               "1]/a/text()").get(),
        book_item['description'] = response.xpath(".//div[@id='product_description']/following-sibling::p/text("
                                                  ")").get(),
        book_item['price'] = response.xpath(".//p[@class='price_color']/text()").get(),

        yield book_item
