import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=1&search_field=name&search_field=company_name&search_field'
                  '=description&items_on_page=20&text=Python&clusters=true&ored_clusters=true&enable_snippets=true'
                  '&hhtmFrom '
                  '=vacancy_search_list',
                  'https://hh.ru/search/vacancy?area=2&search_field=name&search_field=company_name&search_field'
                  '=description&items_on_page=20&text=Python&clusters=true&ored_clusters=true&enable_snippets=true'
                  '&hhtmFrom '
                  '=vacancy_search_list'
                  ]

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    @staticmethod
    def vacancy_parse(response: HtmlResponse):
        name = response.xpath("//h1//text()").get()
        salary = response.xpath("//div[@data-qa='vacancy-salary']//text()").getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)