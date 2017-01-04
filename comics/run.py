#!/usr/bin/python
#coding:utf-8

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.comic import Comics

# 获取setting.py模块的设置
settings = get_project_settings()
process = CrawlerProcess(settings=settings)

# 添加spider,可以多个
process.crawl(Comics)

# 启动爬虫,阻塞知道爬取结束
process.start()
