# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class F6SListItem(scrapy.Item):
    # item from initial list
    company_name = scrapy.Field()
    short_description = scrapy.Field()
    f6s_company_link = scrapy.Field()
    logo_url = scrapy.Field()
    location = scrapy.Field()
    market = scrapy.Field()
    founded = scrapy.Field()
    no_founders = scrapy.Field()
    no_employee = scrapy.Field()
    page_id = scrapy.Field()

class F6SDetailItem(scrapy.Item):
    #item from detail
    company_name = scrapy.Field()
    f6s_company_link = scrapy.Field()
    website_link = scrapy.Field()
    facebook_link = scrapy.Field()
    twitter_link = scrapy.Field()
    linkdin_link = scrapy.Field()
    detail_description = scrapy.Field()
    founders = scrapy.Field()
    inverstors = scrapy.Field()

class F6SFounderItem(scrapy.Item):
    f6s_founder_link = scrapy.Field()
    profile_image = scrapy.Field()
    name = scrapy.Field()
    title = scrapy.Field()
    type = scrapy.Field()
    facebook_link = scrapy.Field()
    linkdin_link = scrapy.Field()
    twitter_link = scrapy.Field()
    skill = scrapy.Field()
    experience = scrapy.Field()






