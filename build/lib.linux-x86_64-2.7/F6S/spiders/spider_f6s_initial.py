#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from lxml import html
import requests

import scrapy
from scrapy.http.request import Request

from ..items import F6SListItem

class F6SCompanyInital(scrapy.Spider):
    name = "f6s_initial"

    def __init__(self):
        self.link = 'https://www.f6s.com/startups?search={%22context%22:%22and%22,%22rules%22:[{%22filter%22:%22location%22,%22operator%22:%22eq%22,%22value%22:{%22type%22:%22country%22,%22object_id%22:%2299%22}}]}&ss=1&sort=popularity&sort_dir=desc&all_startups=1&columns[]=markets&columns[]=location&columns[]=founders&columns[]=founded&columns[]=employees'

        page_id_requests = requests.get(url='http://47.74.130.150/f6s/list-f6spage/',
                                        headers={'Authorization': 'Token 3399a61c385fbc0e9be374fec1f9cb4c5e21fada'})

        page_id_data = json.loads(page_id_requests.text)
        self.page_count = page_id_data.get("page_id")
        if self.page_count:
            self.page_count = self.page_count + 1
            pagination_query = '&page=' + str(self.page_count) + '&page_alt=1'
            self.link = self.link + pagination_query

        else:
            self.page_count = 1

        print "Requesting Page :" , self.page_count

        self.header = {
                'Host': 'www.f6s.com',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

        self.valid_data = lambda v: v[0] if len(v) > 0 else None

    def start_requests(self):
        yield Request(url=self.link,headers=self.header,callback=self.parse)



    def parse(self, response):
        if response.status == 200:
            item = F6SListItem()
            list_data = html.fromstring(response.body)
            results = list_data.xpath("//div[@class='tr csDashboardRow']")
            for result in results:
                column_data = result.xpath("./div[@class='columns']")
                if column_data:
                    # Take individual data
                    company_name = column_data[0].xpath(
                        ".//div[contains(@class, 'profile-name')]/a[@class='main noline']/text()")
                    company_f6s_link = column_data[0].xpath(
                        ".//div[contains(@class, 'profile-name')]/a[@class='main noline']/@href")
                    company_description = column_data[0].xpath(".//div[contains(@class, 'profile-description')]/text()")
                    company_logo = column_data[0].xpath(
                        ".//div[contains(@class, 'profile-img')]/img[contains(@class, 'profile')]/@src")
                    company_location = column_data[0].xpath(".//div[@data-column='Location']/text()")
                    company_market = column_data[0].xpath(".//div[@data-column='Markets']/text()")
                    company_founded = column_data[0].xpath(".//div[@data-column='Founded']/text()")
                    company_founder_number = column_data[0].xpath(".//div[@data-column='Founders']/text()")
                    company_employee_number = column_data[0].xpath(".//div[@data-column='Employees']/text()")

                    # format the data ,convert list to single
                    item["location"] = self.valid_data(company_location)
                    item["company_name"] = self.valid_data(company_name)
                    item["f6s_company_link"] = self.valid_data(company_f6s_link)
                    item["short_description"] = self.valid_data(company_description)
                    item["logo_url"] = self.valid_data(company_logo)
                    item["market"] = self.valid_data(company_market)
                    item["founded"] = self.valid_data(company_founded).replace("\"","")
                    item["no_founders"] = self.valid_data(company_founder_number)
                    item["no_employee"] = self.valid_data(company_employee_number)
                    item["page_id"] = self.page_count
                    yield item


            #next page
            self.page_count = self.page_count + 1
            pagination_query = '&page=' + str(self.page_count) + '&page_alt=1'
            next_url = self.link + pagination_query
            print "Waiting for Page Requesting......"
            if next_url:
                yield Request(url=next_url,headers=self.header,callback=self.parse)

