import re

import scrapy

from scrapy.loader import ItemLoader
from ..items import SaiItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class SaiSpider(scrapy.Spider):
	name = 'sai'
	start_urls = ['https://sai-bank.com/category/blog/']

	def parse(self, response):
		articles = response.xpath('//div[contains(@class,"post-item isotope-item clearfix ")]')
		for article in articles:
			date = article.xpath('.//div[@class="date_label"]/text()').get()
			post_links = article.xpath('.//h2[@class="entry-title"]/a/@href').get()
			yield response.follow(post_links, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//a[@class="next_page"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response,date):
		title = response.xpath('//h1[@class="entry-title"]/text()').get()
		content = response.xpath('//div[@class="the_content_wrapper"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=SaiItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
