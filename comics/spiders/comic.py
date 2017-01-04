#coding:utf-8

import scrapy
import os
import requests
from scrapy.selector import Selector

class Comics(scrapy.Spider):

	name = "comics"

	def start_requests(self):
		urls = ['http://www.xeall.com/shenshi']
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	# 找出所有的漫画url
	def parse(self, response):

		# 请求返回的html源码
		content = Selector(response=response)
		if not content:
			print('parse body error.')
			return

		# 获取单个漫画标签
		com_count = content.xpath("//div[@class='mainleft']/ul/li")

		# 获取单页中所有漫画的url
		comics_url_list = []
		base_url = 'http://www.xeall.com'
		for i in range(len(com_count)):
		    com_url = content.xpath("//div[@class='mainleft']/ul/li[{}]/a/@href".format(i+1)).extract()
		    url = base_url+com_url[0]
		    comics_url_list.append(url)
		    
		print('\n>>>>>>>>>>>>>>>>>>> current page comics list <<<<<<<<<<<<<<<<<<<<')
		print(comics_url_list)

		# 处理当前页每部漫画
		for url in comics_url_list:
			print('>>>>>>>>  parse comics:' + url)
			yield scrapy.Request(url=url, callback=self.comics_parse)

		url_num = content.xpath("//div[@class='mainleft']/div[@class='pages']/ul/li")
		next_url = content.xpath("//div[@class='mainleft']/div[@class='pages']/ul/li[{}]/a/@href".format(len(url_num)-3)).extract()

		# print '总页数: {},下一页: {}'.format(url_num,next_url)

		if next_url:
			next_page = 'http://www.xeall.com/shenshi/' + next_url[0]
			if next_page is not None:
				print('\n------ parse next page --------')
				print(next_page)
				yield scrapy.Request(next_page, callback=self.parse)
				pass
		else:
			print('========= Last page ==========')

	def comics_parse(self, response):
		# 提取每部漫画数据
		content = Selector(response=response)
		if not content:
			print('parse comics body error.')
			return;

		# 当前页数
		page_num = content.xpath("//div[@class='dede_pages']/ul/li[@class='thisclass']/a/text()").extract()

		# 首张图片的url
		current_url = content.xpath("//div[@class='mhcon_left']/ul/li/p/img/@src").extract()

		# 漫画名称
		comic_name = content.xpath("//div[@class='mhcon_left']/ul/li/p/img/@alt").extract()

		print('img url: ' + current_url[0])

		# 将图片保存到本地
		self.save_img(page_num[0], comic_name[0], current_url[0])

		# 下一页图片的url，当下一页标签的href属性为‘#’时为漫画的最后一页
		page_num = content.xpath("//div[@class='dede_pages']/ul/li")
		next_page = content.xpath("//div[@class='dede_pages']/ul/li[{}]/a/@href".format(len(page_num))).extract()

		if next_page == '#':
			print('parse comics:' + comic_name + 'finished.')
		else:
			next_page = 'http://www.xeall.com/shenshi/' + next_page[0]
			yield scrapy.Request(next_page, callback=self.comics_parse)

	def save_img(self, img_mun, title, img_url):
		# 将图片保存到本地
		print('saving pic: ' + img_url)

		# 保存漫画的文件夹
    		document = os.path.join(os.getcwd(),'cartoon')

		# 每部漫画的文件名以标题命名
    		comics_path = os.path.join(document,title)
		exists = os.path.exists(comics_path)
		if not exists:
			print('create document: ' + title)
			os.makedirs(comics_path)

		# 每张图片以页数命名
		pic_name = comics_path + '/' + img_mun + '.jpg'

		# 检查图片是否已经下载到本地，若存在则不再重新下载
		exists = os.path.exists(pic_name)
		if exists:
			print('pic exists: ' + pic_name)
			return

		try:
			user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
			headers = { 'User-Agent' : user_agent }

			response = requests.get(img_url,timeout=30)

			# 请求返回到的数据
			data = response

			with open(pic_name,'wb') as f:
			    for chunk in data.iter_content(chunk_size=1024):
				if chunk:
				    f.write(chunk)
				    f.flush()

			print('save image finished:' + pic_name)

			# urllib.request.urlretrieve(img_url, pic_name)
		except Exception as e:
			print('save image error.')
			print(e)
