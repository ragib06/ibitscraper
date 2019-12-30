import os
import pdb
import zlib
import pathlib
import argparse

import pandas as pd

from scrapy import Spider
from scrapy.http import FormRequest
from scrapy.selector import Selector
from scrapy.http.request import Request
from scrapy.spiders.init import InitSpider
from scrapy.utils.response import open_in_browser


class IbitSpider(InitSpider):
	name = 'ibit_codes'
	
	allowed_domains = ['interviewbit.com']
	base_url = "https://www.interviewbit.com"
	

	def __init__(self, username='', password='', in_file='', out_dir='', ext='', **kwargs):
		self.username = username
		self.password = password
		self.input_file = in_file
		self.out_dir = out_dir
		self.ext = ext
		self.pdf = pd.read_csv(self.input_file)
		self.id_to_code = {}

		self.login_page = "%s/users/sign_in/" % (self.base_url)
		self.start_urls = tuple(self.pdf["url"])
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
		return self.initialized() 


	def parse(self, response):
		hxs = Selector(response)
		code = hxs.xpath('//textarea[@id="editor"]/text()').extract_first()

		problem = response.request.url.split('/')[-2]
		compressed = zlib.compress(code.encode('utf-8'))
		self.id_to_code[problem] = compressed


	def dump_codes(self):
		for index, row in self.pdf.iterrows():
			problem = row["url"].split('/')[-2]
			filename = "%s.%s" % (problem, self.ext)
			target_dir = os.path.join(self.out_dir, row["topic"], row["category"])
			pathlib.Path(target_dir).mkdir(parents=True, exist_ok=True)

			file_path = os.path.join(target_dir, filename)
			with open(file_path, 'w') as f:
				code_str = zlib.decompress(row["code"]).decode("utf-8")
				f.write(code_str)


	def closed(self, reason):
		comp_codes = []
		for url in list(self.pdf["url"]):
			problem = url.split('/')[-2]
			comp_codes.append(self.id_to_code[problem])

		self.pdf["code"] = comp_codes
		self.pdf.to_csv("%s/ibit_codes.csv" % (self.out_dir), index=None)

		self.dump_codes()
		
