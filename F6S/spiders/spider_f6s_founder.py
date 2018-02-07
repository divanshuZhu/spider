import time
import json
import requests
from random import randint
from lxml import html
from fake_useragent import UserAgent

from scrapy.utils.project import get_project_settings
import scrapy
from scrapy.http.request import Request

from ..items import F6SFounderItem

class F6SFounderSpider(scrapy.Spider):
    name = "f6s_founder"

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
        self.link = settings.get('API_URL') + 'list-f6sfounder-link'

        self.valid_data = lambda v: v[0] if len(v) > 0 else None

    def start_requests(self):
        while True:
            paginated_founder_link = self.next_page(self.link)  # list of f6s link of companies
            urls = paginated_founder_link[1]
            next_url = paginated_founder_link[0]
            for url in urls:
                self.header["User-Agent"] = self.ua.random
                yield Request(url=url["f6s_founder_link"], headers=self.header, callback=self.parse,
                              meta={"f6s_founder_link": url["f6s_founder_link"]})
            if next_url:
                self.link = next_url
            else:
                break


    def parse(self, response):
        if response.status == 200:
            item = F6SFounderItem()
            detail_data = html.fromstring(response.body)
            meta = response.meta.copy()
            item["f6s_founder_link"] = meta["f6s_founder_link"]
            item["profile_image"] = self.valid_data(detail_data.xpath(".//div[contains(@class, 'profile-picture')]/img/@src"))
            person_details = self.valid_data(detail_data.xpath("//div[@class='cover-text']"))

            item["name"] = self.valid_data(person_details.xpath(".//h1[@class='cover-title']/text()"))
            item["title"] = self.valid_data(person_details.xpath(".//div[@class='mw cover-blurb inline']/text()"))
            item["type"] = self.valid_data(person_details.xpath(
                ".//div[@class='profile-detail-blocks']/div[contains(@class, 'profile-types-wrapper')]/span/text()"))
            links = self.valid_data(
                person_details.xpath(".//div[@class='profile-detail-blocks']/div[@data-mod-name='links_cover']"))
            # website_link = valid_data(links.xpath(".//a[contains(@class, 'link-website')]/@href"))
            if links:
                item["facebook_link"] = self.valid_data(links.xpath(".//a[contains(@class, 'link-facebook')]/@href"))
                item["linkdin_link"] = self.valid_data(links.xpath(".//a[contains(@class, 'link-twitter')]/@href"))
                item["twitter_link"] = self.valid_data(links.xpath(".//a[contains(@class, 'link-linkedin')]/@href"))
                item["skill"] = detail_data.xpath(".//li[@data-list='skills-list']/text()")
            else:
                item["facebook_link"] = None
                item["linkdin_link"] = None
                item["twitter_link"] = None
                item["skill"] = None

            experience_list = detail_data.xpath(".//div[@id='csWorkHistoryList']/div[@class='person-blk ']")
            item["experience"] = []
            for experience in experience_list:
                company_name = self.valid_data(
                    experience.xpath(".//div[@class='sub-block']/p[@class='t b18']/a[@class='main noline']/text()"))
                postition = self.valid_data(experience.xpath(".//div[@class='sub-block']/p[@class='t b18']//text()[2]"))
                item["experience"].append({"company_name": company_name, "position": postition})

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


