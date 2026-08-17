# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd
import pymysql
from scrapy.exceptions import DropItem
import logging
from scrapy.utils.project import get_project_settings

class ZpPipeline:
    def open_spider(self,spider):
        self.all_items = []
    def process_item(self, item, spider):
        self.all_items.append(item)
        return item
    def close_spider(self,spider):
        df=pd.DataFrame(self.all_items)
        zp_imformation=["job_name","job_news","job_city","job_ex","job_edu","job_company","c_info","c_num","c_tag"]
        etist_culonms=[col for col in zp_imformation if col in df.columns]
        df.to_csv("招聘信息.csv",index=False,columns=etist_culonms)
class MySQLPipeline:
    def open_spider(self,spider):
        settings = get_project_settings()
        self.host=settings.get("MySQL_HOST","localhost")
        self.port=settings.get("MySQL_PORT",3306)
        self.user=settings.get("MySQL_USER","root")
        self.password=settings.get("MySQL_PASSWORD","123456")
        self.db=settings.get("MySQL_DATABASE","zp")
        self.charset=settings.get("MySQL_CHARSET","utf8mb4")
        try:
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.db,
                charset=self.charset,
                use_unicode=True,
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            spider.logger.error(f"连接失败：{e}")
            raise
        self.buffer=[]
        self.BATCH_SIZE=100
    def process_item(self, item, spider):

        # 定义MySQL语句
        sql="""INSERT INTO jobs(
        job_name,
        job_news,
        job_city,
        job_ex,
        job_edu,
        job_company,
        c_info,
        c_num,
        c_tag,
        crawl_time)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s,NOW()
        )"""
        # 从itme里面取出数据组成元组
        values=(
            item.get("job_name",''),
            item.get("job_news",''),
            item.get("job_city",''),
            item.get("job_ex",''),
            item.get("job_edu",''),
            item.get("job_company",''),
            item.get("c_info",''),
            item.get("c_num",''),
            item.get("c_tag",''),
        )
        self.buffer.append(values)
        if len(self.buffer) >= self.BATCH_SIZE:
            self._batch_insert(spider)
        return item
    def _batch_insert(self,spider):
        if not self.buffer:
            return
        sql = """INSERT INTO jobs(
                job_name,
                job_news,
                job_city,
                job_ex,
                job_edu,
                job_company,
                c_info,
                c_num,
                c_tag,
                crawl_time)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s,NOW()
                )"""
        try:
            self.cursor.executemany(sql,self.buffer)
            self.conn.commit()
            spider.logger.info(f"插入{len(self.buffer)}条数据成功")
            self.buffer.clear()
        except Exception as e:
            self.conn.rollback()
            spider.logger.error(e)
            raise
    def close_spider(self,spider):
        if self.buffer:
            self._batch_insert(spider)
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

