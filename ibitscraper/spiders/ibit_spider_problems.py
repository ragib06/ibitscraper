import re
import sys
import pdb
import logging
import argparse

import pandas as pd
from lxml import html

from scrapy.http import FormRequest
from scrapy.selector import Selector
from scrapy.http.request import Request
from scrapy.spiders.init import InitSpider
from scrapy.utils.response import open_in_browser


class IbitSpider(InitSpider):
	name = 'ibit_problems'
	
	allowed_domains = ['interviewbit.com']
	base_url = "https://www.interviewbit.com"
	

	def __init__(self, username='', password='', out_file='', **kwargs):
		self.username = username
		self.password = password
		self.out_file = out_file
		
		self.topics = []
		self.problems_by_topic = {}
		
		self.login_page = "%s/users/sign_in/" % (self.base_url)
		self.front_page = '%s/courses/programming/' % self.base_url

		super().__init__(**kwargs)


	def init_request(self):
		return Request(url=self.login_page, callback=self.login)


	def login(self, response):

		token = response.xpath('//input[@name="authenticity_token"]/@value').extract_first()

		payload = {
			"user[email]": self.username, 
			"user[password]": self.password, 
			"authenticity_token": token
		}

		return FormRequest.from_response(response, formdata=payload, callback=self.check_login_response)


	def check_login_response(self, response):
		if 'Log in to your account' in str(response.body):
			logging.error("Login error, aborting")
			sys.exit(1)
		return Request(url=self.front_page, callback=self.parse_front)


	def parse_front(self, response):
		topic = response.request.url.split('/')[-2]
		hxs = Selector(response)
		
		topic_divs = hxs.xpath("//div[@class='topic-title']")

		for td in topic_divs:
			topic_name = td.xpath("./text()").extract_first().strip().lower()
			topic_name = topic_name.replace("&", "")
			topic_name = re.sub('\s+', ' ', topic_name).strip()
			topic_name = topic_name.replace(" ", "-")
			self.topics.append(topic_name)
		
		self.topics = self.topics[1:-1]
		self.start_urls = tuple('%s/courses/programming/topics/%s/' % (self.base_url, topic) for topic in self.topics)
		
		return self.initialized()


	def parse(self, response):
		topic = response.request.url.split('/')[-2]

		hxs = Selector(response)
		div_problems = html.fromstring(hxs.xpath("//div[contains(@id,'problems')]/div[2]").extract_first())

		left_col, right_col = div_problems.xpath("*")
		categories = left_col.xpath("*") + right_col.xpath("*")

		problems = []

		for cat in categories:
			cat_name = cat.xpath("./div[1]/div[1]/span[1]/text()")[0]
			rows = cat.xpath("./div[1]/div[2]/table/tbody/*")

			for r in rows:
				p_title = r.xpath("./td/a/text()")[0].strip()
				p_url = self.base_url + r.xpath("./td/a/@href")[0].strip()

				problems.append((cat_name, p_title, p_url))

		self.problems_by_topic[topic] = problems


	def closed(self, reason):

		if not self.topics:
			logging.debug("Nothing to process")
			return

		all_problems = {'topic': [], 'category': [], 'title': [], 'url': []}

		for topic in self.topics:
			problems = self.problems_by_topic[topic]

			all_problems['topic'] += ([topic] * len(problems))
			all_problems['category'] += list(map(lambda x: x[0], problems))
			all_problems['title'] += list(map(lambda x: x[1], problems))
			all_problems['url'] += list(map(lambda x: x[2], problems))

		pdf = pd.DataFrame(all_problems)
		pdf = pdf.groupby(["topic"]).apply(lambda x: x.sort_values(['category', 'title'])).reset_index(drop=True)

		pdf.to_csv(self.out_file, index=None)
		
