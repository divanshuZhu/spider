import requests
from lxml import html
import json
from fake_useragent import UserAgent


import scrapy
from scrapy.http.request import Request
from scrapy.utils.project import get_project_settings

from ..items import F6SDetailItem

class F6SCompanyDetailSpider(scrapy.Spider):
    name = "f6s_detail"

    def __init__(self):
        self.ua = UserAgent()

        self.header = {
                'Host': 'www.f6s.com',
                'User-Agent': self.ua.random,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        settings = get_project_settings()
        self.link = settings.get('API_URL') + 'list-f6scompany-link'
        self.valid_data = lambda v: v[0] if len(v) > 0 else None

    def start_requests(self):
        while True:
            paginated_company_link = self.next_page(self.link) # list of f6s link of companies
            urls = paginated_company_link[1]
            next_url = paginated_company_link[0]
            for url in urls:
                self.header["User-Agent"] = self.ua.random
                yield Request(url=url["f6s_company_link"],headers=self.header,callback=self.parse,meta={"f6s_company_link":url["f6s_company_link"]})
            if next_url:
                self.link = next_url
            else:
                break

    def parse(self, response):
        if response.status == 200:
            item = F6SDetailItem()
            detail_data = html.fromstring(response.body)
            meta = response.meta.copy()
            item["f6s_company_link"] = meta["f6s_company_link"]
            item["company_name"] = self.valid_data(detail_data.xpath(
                "//div[@class='profile-details']/div[@class='cover-text']/h1[@class='cover-title']/text()"))
            social_links = self.valid_data(detail_data.xpath("//div[contains(@class, 'profile-links')]"))

            if social_links:
                item["website_link"] = self.valid_data(
                    social_links.xpath(
                        ".//div[contains(@class, 'cover-links')]/a[contains(@class, 'link-website')]/@href"))
                item["facebook_link"] = self.valid_data(social_links.xpath(
                    ".//div[contains(@class, 'cover-links')]/a[contains(@class, 'link-facebook')]/@href"))
                item["twitter_link"] = self.valid_data(
                    social_links.xpath(
                        ".//div[contains(@class, 'cover-links')]/a[contains(@class, 'link-twitter')]/@href"))
                item["linkdin_link"] = self.valid_data(social_links.xpath(
                    ".//div[contains(@class, 'cover-links')]/a[contains(@class, 'link-linkedin')]/@href"))

            item["detail_description"] = self.valid_data(
                detail_data.xpath("//div[contains(@id, 'description-expanded')]/text()"))

            founders_list = self.valid_data(detail_data.xpath(
                "//div[contains(@data-mod-name, 'connections_founders')]"))  # /a[contains(@class, 'main noline')]/@href"))
            if founders_list:
               item["founders"] = founders_list.xpath(".//a[contains(@class, 'main noline')]/@href")

            investors_list = detail_data.xpath(
                "//div[contains(@id, 'connections-investors')]/div[contains(@data-list, 'connections-list')]")
            item["inverstors"] = []
            if investors_list:
                for investor in investors_list:
                    investor_name = self.valid_data(investor.xpath(".//a[contains(@class, 'main noline')]/strong/text()"))
                    investor_link = self.valid_data(investor.xpath(".//a[contains(@class, 'main noline')]/@href"))
                    item["inverstors"].append({"name": investor_name, "f6s_link": investor_link})

            yield item


    def next_page(self,url):
        settings = get_project_settings()
        token = settings.get('API_TOKEN')
        token = 'Token ' + token
        list_request = requests.get(url=url,headers={'Authorization': token})
        list_data = json.loads(list_request.text)
        next_url =  list_data.get("next")
        list_link = list_data.get("results")
        return [next_url,list_link]


