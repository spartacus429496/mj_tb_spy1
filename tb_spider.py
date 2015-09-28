#!/usr/bin/env python
#-*- coding: UTF-8 -*-

import HTMLParser
import string
import time
import json
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from tb_items import TaobaoShop, shop_commodity

class Request():
    def __init__(self, url, callback):
        self.url = url
        self.callback = callback

class TbSpider():
    login_URL = 'https://login.taobao.com/member/login.jhtml'
    current_shopid = 36326929
    drive_choose = 2
    last_url = ''

    def __init__(self):
        if self.drive_choose==1:
            self.driver = webdriver.Firefox()
        elif self.drive_choose==2:
            self.driver = webdriver.PhantomJS()

        # self.driver = webdriver.PhantomJS()
        # self.driver = webdriver.Firefox()
        # self.driver = webdriver.PhantomJS(service_args=['--load-images=no'])

        self.driver.set_window_size(1024, 768)
        # self.driver.set_page_load_timeout(10)
        # self.driver.set_script_timeout(1)
        self.htmlparser = HTMLParser.HTMLParser()

    def run(self):
        success = self.login()
        if success:
            self.start_crawl_task(Request(self.next_task_url(), self.shop_basic_info_parse))

    def get_checkcode(self):
        checkcode = ''
        try:
            checkcode_url = self.driver.find_element_by_id("J_StandardCode_m").get_attribute('data-src')
            checkcode_url_1 = self.driver.find_element_by_id("J_StandardCode_m").get_attribute('src')
        except:
            print "验证码链接提取错误"

        if checkcode_url:
            print "src %s" % checkcode_url_1
            print checkcode_url
            checkcode = raw_input("请输入验证码:")

        return checkcode

    def submit_login_form(self, username, password):
        username_el = self.driver.find_element_by_id("TPL_username_1")
        password_el = self.driver.find_element_by_id("TPL_password_1")

        username_el.clear()
        username_el.send_keys(username)

        password_el.clear()
        password_el.send_keys(password)

        time.sleep(1)

        self.driver.save_screenshot('checkcode.png')
        checkcode = self.get_checkcode()

        if checkcode:
            self.driver.find_element_by_id("J_CodeInput_i").send_keys(checkcode)

        self.driver.find_element_by_id("J_SubmitStatic").submit()
        # self.driver.save_screenshot('after_submit.png')

        ret = False
        for i in xrange(10, 0, -1):
            time.sleep(1)
            print i
            if not (self.login_URL in self.driver.current_url):
                ret = True
                break 

        return ret

    # def login(username='mengjie@safefw.com', password='zxsoft520'):
    def login(self, username='15715513873', password='w543478'):
        print '开始登录....'

        self.driver.get(self.login_URL)

        success = self.submit_login_form(username, password)

        while not success:
            try:
                err_msg = self.driver.find_element_by_xpath("//div[@id='J_Message']//p[@class='error']").text
                if err_msg:
                    print u"页面错误信息:"
                    print err_msg
            except:
                if not (self.login_URL in self.driver.current_url):
                    success = True
                    break

            a = raw_input("本次登录不成功，是否继续? N/y:")
            if not a == 'Y' and not a == 'y':
                break

            success = self.submit_login_form(username, password)

        if not success:
            print '登录失败'
            return False
        else:
            print "登录成功"
            print u"重定向到: %s" % self.driver.current_url
            return True

        # self.driver.quit()

    def start_crawl_task(self, request):
        # self.driver.set_page_load_timeout(5)
        while request:
            try:
                self.driver.get(request.url)
            except:
                print "获取页面超时"
                time.sleep(2)
                # request = Request(self.next_task_url(), self.shop_basic_info_parse)
            request = request.callback()

    def next_task_url(self):
        self.current_shopid += 1
        url = "https://shop%ld.taobao.com" % self.current_shopid
        print "下一个店铺的地址 %s" % url
        return url

    def current_task_url(self):
        # self.current_shopid += 1
        url = "https://shop%ld.taobao.com" % self.current_shopid
        print "当前店铺的地址 %s" % url
        return url

    def shop_basic_info_parse(self):
        resp_url = self.driver.current_url

        if ("noshop.htm" in resp_url) or ("error1.html" in resp_url) \
            or ("guang.taobao" in resp_url):
            # 当前url无效， 获取下一个任务
            print u"无此店铺"
            return Request(self.next_task_url(), self.shop_basic_info_parse)
        else:
            t = self.driver.find_elements(By.XPATH, '//title')
            if len(t) == 0:
                print "页面错误"
                return Request(self.next_task_url(), self.shop_basic_info_parse)

            print u"解析店铺主页面 %s" % resp_url

            t = t[0].get_attribute("innerHTML")

            self.shop = TaobaoShop(shop_number=self.current_shopid, shop_url=resp_url)

            if not t:
                print "解析主页面错误"
                return Request(self.next_task_url(), self.shop_basic_info_parse)

            if  t.find(u"Tmall.com") >= 0:
                self.shop.shop_classify = 1
                n = self.driver.find_element_by_xpath("//a[@class='slogo-shopname']/*").get_attribute("innerHTML")
                l = self.driver.find_element_by_xpath("//*[@id='dsr-ratelink']").get_attribute("value")

                if (not n) or (not l):
                    print "解析天猫店铺基本信息错误"
                    return Request(self.next_task_url(), self.shop_basic_info_parse)

                self.shop.shop_name = n[0]
                self.shop.shop_detail_url = "https:" + l[0]
                # return Request(l, self.parse_tmall_detail)
                return

            else:
                url = self.driver.find_elements(By.XPATH, '//span[@class="shop-rank"]//a')
                if len(url) == 0:
                    return Request(self.next_task_url(), self.shop_basic_info_parse)

                url = url[0].get_attribute("href")

                self.shop.shop_classify = 0
                self.shop.shop_detail_url = url

                shop_name = self.driver.find_elements(By.XPATH, "//a[@class='shop-name']/*")
                if len(shop_name) == 0:
                    return Request(self.next_task_url(), self.shop_basic_info_parse)

                self.shop.shop_name = shop_name[0].get_attribute("innerHTML")
                # self.shop.output()
                # return Request(self.next_task_url(), self.shop_basic_info_parse)
                return Request(url, self.parse_tbshop_detail)

    def parse_tbshop_detail(self):
        print u"解析店铺详细信息 %s" % self.driver.current_url

        if "anti_Spider" in self.driver.current_url:
            print "Oohs!"
            return

        # 解析好评率
        rate = self.driver.find_element_by_xpath("//*[@class='tb-rate-ico-bg ico-seller']/em").get_attribute("innerHTML")
        if rate:
            rate = rate.split(u"：")
            if len(rate) == 2:
                try:
                    rate = string.atof(rate[1][:-1])
                except:
                    print "malform string: %s" % rate
                else:
                    self.shop.shop_credit = rate
        else:
            print "解析好评率错误"

        # 解析建店时间
        startdate = self.driver.find_element_by_xpath("//input[@id='J_showShopStartDate']").get_attribute("value")

        if startdate:
            self.shop.shop_create_time = startdate
        else:
            print "解析建店时间错误"

        # 解析店主名称
        owner = self.driver.find_element_by_xpath("//div[@class='title']/a").get_attribute("innerHTML")
        if owner:
            self.shop.shop_owner = owner
        else:
            print "解析店主名称错误"

        # 解析当前主营
        trade_key = u"当前主营"
        # 解析所在地区
        location_key = u"所在地区"

        els = re.findall("<li>(.*)</li>", self.driver.page_source)
        for el in els:
            if el.find(trade_key) >=0:
                el = re.findall("<a href=\".*\">(.*)</a>", el)
                if len(el) == 1:
                    el = self.htmlparser.unescape(el[0]) # 去掉HTML的转义字符
                    self.shop.shop_trade_range = el.strip()
                else:
                    print "解析当前主营错误"

            elif el.find(location_key) >= 0:
                el = el.split(u"：")
                if len(el) == 2:
                    self.shop.shop_location = self.htmlparser.unescape(el[1]).strip()
                else:
                    print "解析所在地区错误"
                break

        # 解析卖家信用
        credit_key = u"卖家信用："
        start = self.driver.page_source.find(credit_key)
        if start >= 0:
            start += len(credit_key)
            end = start
            while 1:
                if self.driver.page_source[end] in '\r\n\<\ ':
                    break
                end += 1
            try:
                credit = string.atoi(self.driver.page_source[start:end].strip())
                self.shop.shop_credit = credit
            except:
                print u"解析信用错误"

        if self.shop.shop_location == "":
            # 如果在前面没有解析出地址(可能是店家没有写),
            # 就从这家店铺商品的收货地址取得其店铺地址
            url = "https://list.taobao.com/itemlist/default.htm?nick=%s&_input_charset=utf-8&json=on&callback=jsonp161" \
                   % self.shop.shop_owner.encode("utf8")
            return Request(url, self.parse_location_by_shipping_addr)
        else:
            self.shop.output()

            if self.shop.shop_location.find(u"合肥") < 0:
                return Request(self.next_task_url(), self.shop_basic_info_parse)

            # url = "https://list.taobao.com/itemlist/default.htm?nick=%s&style=list&_input_charset=utf-8&json=on&callback=jsonp731" \
            #        % self.shop['shop_owner'].encode("utf8")
            # return Request(url, callback=self.parse_commodity)
            return Request(self.next_task_url(), self.shop_basic_info_parse)
            # yield self.shop

    # 通过店铺商品的收货地址来得到店铺地址
    def parse_location_by_shipping_addr(self):
        print "parse_location_by_shipping_addr"
        
        resp_url = self.driver.current_url
        if "anti_Spider" in resp_url:
            print "Oohs ！！！遭遇反爬虫"
            return Request(self.next_task_url(), self.shop_basic_info_parse)
        else:
            json_set = self.decode_tb_json(self.driver.page_source)
            if "itemList" in json_set:
                itemlist = json_set['itemList']
                print "==========================="
                if itemlist != None and len(itemlist) != 0:
                    self.shop.shop_location = itemlist[0]['loc'].strip()

            self.shop.output()
            return Request(self.next_task_url(), self.shop_basic_info_parse)

    def decode_tb_json(self, data):
        json_set = set()

        start = data.find("(")
        end =   data.rfind(")")
        if start < 0 or end < 0:
            print "无法识别json文件"
        else:
            try:
                data = data[start+1:end]
            except:
                print "json 字符集错误"
            else:
                json_set = json.loads(data)
        return json_set

if __name__ == "__main__":
    spider = TbSpider()
    spider.run()