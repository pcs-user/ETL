import scrapy
from ..items import ZpItem
class ZptextSpider(scrapy.Spider):
    name = "zptext"
    allowed_domains = ["www.zhaopin.com"]
    start_urls = []
    city_id=["jl530","jl538","jl763"]
    for city in city_id:
        for i in range(1,6):
            url=f"https://www.zhaopin.com/sou/{city}/kw01O00U80EG06G03F01N74B46DDEUAUGBBO40/p{i}"
            start_urls.append(url)

    def parse(self, response):
        try:
            res=response.xpath('//*[@id="positionList-hook"]/div/div[1]/div')
            for i in res:
                item=ZpItem()
                job_box=i.xpath('.//div[@class="jobinfo"]')
                item["job_name"]=job_box.xpath('.//div[@class="jobinfo__name-row"]/a/text()').get().strip()
                item["job_news"]=job_box.xpath('.//p/text()').get().strip()
                item['job_city']=job_box.xpath('.//span/text()').get().strip()
                item["job_ex"]=job_box.xpath('./div[last()]/div[2]/text()').get().strip()
                item["job_edu"]=job_box.xpath('./div[last()]/div[3]/text()').get().strip()
                job_company=i.xpath('.//div[@class="companyinfo"]')
                item['job_company']=job_company.xpath('.//a/text()').get().strip()
                job_info=job_company.xpath('./div[2]/div')
                if len(job_info)==3:
                    item["c_info"]=job_company.xpath('./div[2]/div[1]/text()').get().strip()
                    item["c_num"]=job_company.xpath('./div[2]/div[2]/text()').get().strip()
                    item["c_tag"]=job_company.xpath('./div[2]/div[3]/text()').get().strip()
                else:
                    item["c_info"]=""
                    item["c_num"]=job_company.xpath('./div[2]/div[1]/text()').get().strip()
                    item["c_tag"]=job_company.xpath('./div[2]/div[2]/text()').get().strip()
                yield item
        except Exception as e:
            self.logger.error(f"爬取失败{e}",exc_info=True)
            raise