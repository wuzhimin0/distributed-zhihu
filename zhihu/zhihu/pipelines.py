# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline
from scrapy.http import Request
from pymongo import MongoClient
from scrapy.conf import settings
class ZhihuPipeline(object):
    def __init__(self):
        self.db = MongoClient(settings["MONGODB_HOST"],settings["MONGODB_PORT"])
        self.sheet = self.db["zhihu"]["zhihu"]
    def process_item(self, item, spider):
        # self.sheet.insert(dict(item))
        # 如果没有匹配的content，那么就插入一条新的item，如果有匹配的content，那么就更新匹配的那条item，True可以保证命令的正确执行
        self.sheet.update({'content': item['content']}, {'$set': dict(item)}, True)
        return item
    def close_spider(self,spider):
        self.db.close()
# 写存储图片的piplines管道，继承自ImagesPipeline类，存图片是，获取的url最好是放在列表里面
class ImagePipeline(ImagesPipeline):
    # 写存储图片的函数
    def get_media_requests(self, item, info):
        # 循环每一张图片地址下载，若传过来的不是集合则无需循环直接yield
        for image_url in item['image']:
            if image_url:
                yield Request(image_url, meta={"name":item["answer_name"]})
    # 重写图片存放的目录名及文件名的函数
    def file_path(self, request, response=None, info=None):
        name = request.meta["name"]
        # 提取url后面的图片名称
        image_guid = request.url.split("/")[-1]
        # 分文件存储的关键，{0}对应着name，{1}对应着image_guid
        filename = u'{0}/{1}'.format(name, image_guid)
        return filename
    # 将图片的地址从网址变成本地的路径
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        item['image'] = image_paths
        return item
# 音乐视频文件下载管道
class VideoPipeline(FilesPipeline):
    # 自定义文件下载管道
    def get_media_requests(self, item, info):
        # 根据文件的url逐一发送请求
        for video_url in item['video']:
            if video_url:
                yield Request(url=video_url, meta={"name":item["answer_name"]})
    def file_path(self, request, response=None, info=None):
        name = request.meta["name"]
        # 提取url后面的图片名称
        image_guid = request.url.split("/")[-1] + ".mp4"
        # 分文件存储的关键，{0}对应着name，{1}对应着image_guid
        filename = u'{0}/{1}'.format(name, image_guid)
        return filename
    def item_completed(self, results, item, info):
        video_paths = [x['path'] for ok, x in results if ok]
        item['video'] = video_paths
        return item