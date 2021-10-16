import scrapy
import sys
import os
import re
import random
import time
import json
import logging
import parse
from spider_911mjw.items import VideoItem
from urllib.parse import urlparse, urljoin
from datetime import datetime
from scrapy.exceptions import NotConfigured

sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))

class VideosSpider(scrapy.Spider):
    name = 'videos'
    page_path_format = 'index{page_index}.html'
    spider_title_list = ['美剧', '电影', '纪录片', '真人秀']

    def __init__(self, base_url='https://www.911mjw.com/', page_limit_count=1, video_limit_count=-1, *args, **kwargs):
        super(VideosSpider, self).__init__(*args, **kwargs)
        self.base_url = base_url
        self.start_urls = []
        if base_url:
            self.start_urls.append(base_url)
        self.page_limit_count = int(page_limit_count)
        self.video_limit_count = int(video_limit_count)

    def parse(self, response):
        self.logger.info(f'base_url: {self.base_url}, page_limit_count: {self.page_limit_count}, video_limit_count: {self.video_limit_count}')
        a_list = response.xpath('//*[@class="nav"]/li/a')
        for a_selector in a_list:
            top_title = a_selector.css('::text').get().strip()
            if top_title in self.spider_title_list:
                base_page_path = a_selector.attrib["href"]
                yield response.follow(a_selector, self.parse_first_videos_page, cb_kwargs={"top_title": top_title, 'base_page_path': base_page_path}, dont_filter=True)
            else:
                self.logger.warning(f'ignore title {top_title}')

    def parse_page_count(self, response):
        page_count_str = response.css('.pagination').xpath('ul/li[last()]').css('::text').get()
        res = parse.findall('{:d}', page_count_str)
        page_count = -1
        if res:
            for c in res:
                page_count = c[0]
        if page_count < 0:
            self.logger.warning(f'parse page count failed, set page count is 1')
            page_count = 1
        return page_count

    def get_page_url(self, base_page_path, page_index):
        return urljoin(urljoin(self.base_url, base_page_path), self.page_path_format.format(page_index=page_index))

    def parse_first_videos_page(self, response, top_title, base_page_path):
        page_index = 1
        page_count = self.parse_page_count(response)
        self.logger.info(f'found title {top_title}, page_path: {base_page_path}, page_count: {self.page_limit_count}/{page_count}')
        while page_index <= page_count and (self.page_limit_count < 0 or page_index <= self.page_limit_count):
            page_url = self.get_page_url(base_page_path, page_index)
            yield scrapy.Request(page_url, self.parse_videos_page, cb_kwargs={"top_title": top_title}, dont_filter=True)
            page_index += 1

    def parse_season_id(self, path):
        season_id = 0
        res = parse.findall('Season-{:d}', path)
        if res:
            for c in res:
                season_id = c[0]
        return season_id

    def parse_videos_page(self, response, top_title):
        movie_list = response.css('.u-movie')
        movie_count = 0
        self.logger.info(f'parse video url: {response.url}, found movie count: {self.video_limit_count}/{len(movie_list)}')
        for movie_selector in movie_list:
            movie_count += 1
            a_info = movie_selector.xpath('a')
            movie_name = a_info.attrib['title']
            movie_path = a_info.attrib['href']
            movie_url = urljoin(self.base_url, movie_path)
            item = VideoItem()
            item['id'] = os.path.basename(movie_path)
            if item['id'].endswith('.html'):
                item['id'] = item['id'][:-5]
            item['name'] = movie_name
            item['url'] = movie_url
            item['path'] = movie_path
            item['status'] = '完结'
            if movie_selector.css('.zhuangtai > span::text').get():
                item['status'] = movie_selector.css('.zhuangtai > span::text').get()
            yield response.follow(movie_path, self.parse_video_info, cb_kwargs={"top_title": top_title, "item": item, "id": item["id"]})
            if self.video_limit_count >= 0 and movie_count >= self.video_limit_count:
                break

    def parse_video_info(self, response, top_title, item, id):
        video_info_text_list = []
        ori_video_info_text_list = []
        info_map = {}
        sep = '\r\n'
        for t in response.css('.video_info ::text'):
            ori_video_info_text_list.append(t.get())
        ori_video_info_text_list.append('\r\n')
        i = 0
        while i < len(ori_video_info_text_list):
            if ori_video_info_text_list[i].strip(' \t') == sep:
                i += 1
                continue
            key = ori_video_info_text_list[i].strip()
            key = key.replace('：', ':')
            if key.endswith(':'):
                video_info_text_list.append(key.strip(':'))
                if ori_video_info_text_list[i + 1] == sep:
                    video_info_text_list.append('')
                    i += 2
                else:
                    value = ori_video_info_text_list[i + 1].strip().strip(':')
                    index = value.find('IMDb')
                    if index >= 0:
                        video_info_text_list.append(value[:index].strip())
                        imdb_str = value[index:].strip()
                        index = imdb_str.find(':')
                        if index >= 0:
                            video_info_text_list.append(imdb_str[:index+1].strip().strip(':'))
                            video_info_text_list.append(imdb_str[index+1:].strip().strip(':'))
                        else:
                            video_info_text_list.append('IMDb')
                    else:
                        video_info_text_list.append(value)
                    i += 2
            else:
                try:
                    new_key, new_value = key.split(':')
                    new_key = new_key.strip()
                    new_value = new_value.strip()
                    video_info_text_list.append(new_key.strip())
                    video_info_text_list.append(new_value.strip())
                except Exception as e:
                    self.logger.error(f'parse key failed({e}), key({key}), url: {item["url"]}, {i}')
                    self.logger.error(f'video_info1: {video_info_text_list}')
                    self.logger.error(f'video_info2: {ori_video_info_text_list}')
                i += 1
        if len(video_info_text_list) % 2:
            self.logger.error(f'{item["name"]}, video_info_text_list: {video_info_text_list}, ori: {ori_video_info_text_list}')
        video_img_url = response.css('.video_img img').attrib['src']
        item['description'] = ''
        if response.css('.jianjie ::text').get():
            item['description'] = response.css('.jianjie ::text').get().strip()
        item['season_id'] = self.parse_season_id(item['path'])
        item["img_url"] = video_img_url
        item['video_count'] = 0
        item['score'] = 0.0
        info_name = {
            '导演': 'director',
            '主演': 'starring',
            '国家/地区': 'country_region',
            '语言': 'language',
            '首播': 'premiere',
            '季数': 'season_id',
            '集数': 'video_count',
            '又名': 'alias',
            'IMDb': 'imdb_code',
            'IMDb编码': 'imdb_code',
            '评分': 'score',
            '单集时长': 'duration',
            '片长': 'duration',
            '编剧': 'screenwriter',
            '上映日期': 'release_date',
            '类型': 'tags',
            '官方网站': 'official_website',
        }
        i = 0
        while i < len(video_info_text_list):
            key = video_info_text_list[i].strip(':')
            value = video_info_text_list[i + 1]
            if key in info_name:
                if info_name[key] in item.keys():
                    if isinstance(item[info_name[key]], int):
                        try: 
                            item[info_name[key]] = int(value)
                        except:
                            item[info_name[key]] = 0
                    elif isinstance(item[info_name[key]], float):
                        try: 
                            item[info_name[key]] = float(value)
                        except:
                            item[info_name[key]] = 0.0
                    else:
                        item[info_name[key]] = value
                else:
                    item[info_name[key]] = value
            else:
                self.logger.error(f'not found video info key({key}), value({value}), url: {item["url"]}')
                self.logger.error(f'video_info1: {video_info_text_list}')
                self.logger.error(f'video_info2: {ori_video_info_text_list}')
            i += 2
        item['videe_url_info_list'] = []
        li_selector = response.css('#download-list > li')
        for li in li_selector:
            name = li.attrib['title'].strip()
            ed2k_url = ''
            magnet_url = ''
            for a in li.css('a'):
                if 'ed2k' in a.attrib['href']:
                    ed2k_url = a.attrib['href'].strip()
                elif 'magnet' in a.attrib['href']:
                    magnet_url = a.attrib['href'].strip()
            info = {
                'ed2k_url': ed2k_url,
                'magnet_url': magnet_url,
                'name': name,
            }
            item['videe_url_info_list'].append(info)
        if not 'imdb_code' in item.keys() or not item['imdb_code']:
            self.logger.debug(f'not found imdb code, url: {item["url"]}')
            self.logger.debug(f'video_info1: {video_info_text_list}')
            self.logger.debug(f'video_info2: {ori_video_info_text_list}')
        return item
