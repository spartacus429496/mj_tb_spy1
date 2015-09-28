# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

class shop_commodity():
    shop_number = 0
    commodity_name = ""
    commodity_id = 0
    commodity_url = ""
    commodity_price = ''
    commodity_promo_price = ''
    commodity_sales = 0
    commodity_stock = 0
    commodity_comment = ''

class TaobaoShop():
    def __init__(self, **kwags):
        self.__dict__ = kwags

    def output(self):
        for property, value in vars(self).iteritems():
            print property, ":", value

# common filed
    shop_number = 0
    shop_seller_id = 0
    shop_classify = 0
    shop_name = ''
    shop_owner = ''
    shop_url = ''
    shop_detail_url = ''
    shop_location = ''
    shop_trade_range = ''
    shop_commodity_list = []

# tmall    
    shop_commany_name = ''
    shop_telephone = ''
# taobao
    shop_create_time = ''
    shop_popularity = ''
    shop_credit = ''