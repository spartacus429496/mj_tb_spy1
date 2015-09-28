#!/usr/bin/env python
#-*- coding: UTF-8 -*-

from tb_spider import TbSpider, Request

t = TbSpider()
r = Request(t.next_task_url(), t.shop_basic_info_parse)
t.start_crawl_task(r)