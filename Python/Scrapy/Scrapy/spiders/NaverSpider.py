import sys
from os.path import dirname, realpath

# parent_dir = dirname(dirname(realpath(__file__)))
# sys.path.append(parent_dir)

# from ....io.ninei.tools.tool import LOG_COLOR

import scrapy
from scrapy import Spider, Request

from .. import items


# Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36

class NaverSpider(Spider):
    agent = {"User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    name = "NaverSpider"

    ZenRawAPIKey = "a9409a58410f51685ecc908d716db5e2df215749"

    proxies = {
        "http": "socks5://127.0.0.1:9050",
        "https": "socks5://127.0.0.1:9050",
    }
    
    # 크롤링 시작 함수
    def start_requests(self):
        url = "https://search.shopping.naver.com/product/84500857369"
        yield scrapy.Request(url=url, proxies=proxies, callback=self.parse_start, headers=self.agent)

    # 크롤링 결과 콜백
    def parse_start(self, response):
        # productURL = "https://m.place.naver.com/restaurant/38415392/home"
        productURL = "https://search.shopping.naver.com/product/84500857369"
        # data_no = response.xpath('//*[@id="__next"]/div/div[2]/div[1]/div/div[1]/div').getall()
        # data_no = response.xpath('//*[@id="__next"]/div/div[2]/div[1]/div/div[3]/div/div/div[3]/div[2]/div').getall()
        # data_no = response.xpath('//*[@id="__next"]/div/div[2]/div[1]/div').getall()
        # data_no = response.xpath('//*[@id="app-root"]/div/div/div/div[5]/div/div[2]/div[1]/div/div[3]/div/span[1]/text()').getall()
        # data_no = response.xpath('//*[@id="app-root"]/div/div/div/div[5]/div/div[2]/div[1]/div/div[3]/div/span[1]/text()').get()
        print(response)
        data_no = response.xpath('//*[@id="wrap"]/div[2]/img').get()
        # print(LOG_COLOR.WARNING + data_no + LOG_COLOR.ENDC)
        print(data_no)
        # for d in data_no:
        #     url = productURL + d
        #     yield scrapy.Request(url, self.parse_items)

            
    # # 상세 페이지 크롤링ß
    # def parse_items(self, response):
    #     item = items.NaverItem()
    #     item['contentsName'] = response.xpath('//*[@id="__next"]/div/div[2]/div[1]/ul/li[1]/div/div[2]/button/div/div[1]').get().strip()
    #
    #     print("ContentName: " + item['contentsName'])
    #
    #     yield item
