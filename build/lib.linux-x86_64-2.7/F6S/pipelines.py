# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import requests
import json

from scrapy.utils.project import get_project_settings

class F6SPipeline(object):
    def process_item(self, item, spider):
        settings = get_project_settings()
        token = settings.get('API_TOKEN')
        token = 'Token ' + token
        if spider.name == 'f6s_initial':
            save_initial_url = settings.get('API_URL') + 'save-f6scompany-initial'
            data = json.dumps({"scrapy":item.__dict__})
            save = requests.post(url=save_initial_url, data={"data":data},
                          headers={'Authorization': token})
            print save.text
            return item

        elif spider.name == 'f6s_detail':
            save_detail_url = settings.get('API_URL') + 'save-f6scompany-details'
            data = json.dumps({"scrapy": item.__dict__})
            save = requests.post(url=save_detail_url, data={"data": data},
                                 headers={'Authorization': token})
            print save.text
            return item

        else:
            save_initial_url = settings.get('API_URL') + 'save-f6sfounder'
            data = json.dumps({"scrapy": item.__dict__})
            save = requests.post(url=save_initial_url, data={"data": data},
                                 headers={'Authorization': token})
            print save.text
            return item

