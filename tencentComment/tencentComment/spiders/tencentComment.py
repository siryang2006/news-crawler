# -*- coding: utf-8 -*-
import logging

import scrapy
from bs4 import BeautifulSoup
from scrapy import Request

from tencent.utils.common import get_now_time
from tencent.utils.global_list import *
from tencentComment.items import TencentCommentItem


class TencentcommentSpider(scrapy.Spider):
    name = 'tencentComment'
    allowed_domains = [NEWS, NEW, SOCIETY, MIL, TECH, ENT, FINANCE, SPORTS]
    start_urls = ["http://new.qq.com/omn/20180511/20180511A04WBW.html"]

    def parse(self, response):
        """
        腾讯新闻评论爬虫主要逻辑
        :param response:
        :return:
        """
        url_list = ["http://new.qq.com/omn/20180511/20180511A04WBW.html",
                    "http://new.qq.com/omn/20180510/20180510A1DSGA.html"]
        # 过滤
        # url_list = get_pre_week_url_list()
        for url in url_list:
            yield Request(url=url, callback=self.parse_detail)

    def parse_detail(self, response):
        tencent_item = TencentCommentItem()
        soup = BeautifulSoup(response.body.decode("utf-8"), "html.parser")

        create_date = get_now_time()
        url = response.url
        content = ""

        if len(soup.select("title")) != 0:
            title = response.url
            if len(soup.select("#J_ShortComment .comment"))>0:
                content_list = soup.select("#J_ShortComment .comment .comment-block .comment-content")
                reply_list = soup.select("#J_ShortComment .comment .comment-block .reply-content")
                # 评论内容获取
                for element in content_list:
                    if not element.text.endswith(("。", "！", "？")):
                        content = content + element.text + "。"
                    else:
                        content = content + element.text

                # 回复内容获取
                for element in reply_list:
                    element.span.decompose()
                    if not element.text.endswith(("。", "！", "？")):
                        content = content + element.text + "。"
                    else:
                        content = content + element.text

            tencent_item["title"] = title
            tencent_item["create_date"] = create_date
            tencent_item["url"] = url
            tencent_item["content"] = content

            if (len(title) > 0 & (len(content) > 0)):
                return tencent_item
            else:
                logging.log(logging.ERROR, url)
                return None
