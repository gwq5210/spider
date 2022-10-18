import re
import scrapy
from urllib.parse import urljoin
from spider_mds.items import M3u8Item


class M3u8Spider(scrapy.Spider):
    name = 'm3u8'

    def __init__(self, settings=None, *args, **kwargs):
        super(M3u8Spider, self).__init__(*args, **kwargs)
        self.base_url = settings.get('BASE_URL', '')
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        self.m3u8_base_url = settings.get('M3U8_BASE_URL', '')
        if not self.m3u8_base_url.endswith('/'):
            self.m3u8_base_url += '/'
        self.start_urls = []
        self.page_path_format = "/page/{page_index}"
        self.m3u8_path_format = "/videos/{video_id}/index.m3u8"
        self.token_regex = re.compile(r"var *token *= *\"(.*)\";")
        if self.base_url:
            self.start_urls.append(self.base_url)
        self.page_limit_count = settings.getint('PAGE_LIMIT_COUNT', -1)
        self.scrapy_category_name = settings.get('SCRAPY_CATEGORY_NAME', [])

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(settings=crawler.settings, *args, **kwargs)
        spider._set_crawler(crawler)
        return spider

    def get_page_url(self, base_url, page_index):
        if page_index < 0:
            return ""
        else:
            return base_url + self.page_path_format.format(page_index=page_index)

    def hit_category(self, category_name):
        for category in self.scrapy_category_name:
            if category.lower() == 'all':
                return True
        for category in self.scrapy_category_name:
            if category.lower() in category_name.lower():
                return True
        return False

    def parse(self, response):
        self.logger.info(f"url: {response.url}, page_limit_count: {self.page_limit_count}, scrapy_category_name: {self.scrapy_category_name}")
        li_list = response.xpath("//*[@class='sitenav']/ul/li")[1:-2]
        for li in li_list:
            a_tags = li.css("a")
            for a in a_tags:
                category_name = a.css("::text").get()
                url = a.attrib["href"]
                if not url or url == "#":
                    self.logger.warning(f'category {category_name} url empty')
                    continue
                if not self.hit_category(category_name):
                    self.logger.warning(f"ignore category {category_name}")
                    continue
                self.logger.info(f"found category {category_name}, url {url}")
                yield self.request_category_page(url, category_name, 1)

    def request_category_page(self, base_url, category_name, page_index):
        page_url = self.get_page_url(base_url, page_index)
        if (not page_url) or (self.page_limit_count > 0 and page_index > self.page_limit_count):
            return
        self.logger.info(f"request {page_url} videos")
        return scrapy.Request(page_url, self.parse_category_page, cb_kwargs={"category_name": category_name, "base_url": base_url, "page_index": page_index}, dont_filter=True)

    def has_next_page(self, response):
        return '下一页' in response.text

    def parse_category_page(self, response, category_name, base_url, page_index):
        self.logger.info(f"category_name {category_name}, response url {response.url}, page index {page_index}")
        article_list = response.xpath("//*[@class='excerpts-wrapper']//article")
        for article_tag in article_list:
            a_tag = article_tag.xpath("h2/a")[0]
            img_tag = article_tag.css("img")[0]
            item = M3u8Item()
            item['name'] = a_tag.css("::text").get()
            item['img_url'] = img_tag.attrib["data-src"]
            video_url = a_tag.attrib["href"]
            item['page_url'] = video_url
            item['category'] = category_name
            self.logger.info(f"{item['name']}, {video_url}, {item['img_url']}")
            yield scrapy.Request(video_url, self.pase_video_page, cb_kwargs={"category_name": category_name, "item": item}, dont_filter=False)
        if self.has_next_page(response):
            yield self.request_category_page(base_url, category_name, page_index + 1)
        else:
            self.logger.info(f'category_name {category_name} page done, page_index: {page_index}')

    def parse_watch_count(self, count_text):
        if not count_text:
            return 0
        count_map = {
            'K' : 1000,
            'W' : 10000,
        }
        if not count_text[-1] in count_map:
            self.logger.info(f'parse watch count {count_text} failed')
            return 0
        count = 0
        for c in count_text[:-1]:
            if c == '.':
                continue
            count = count * 10 + int(c)
        count *= count_map[count_text[-1]]
        return count

    def parse_watch_count_text(self, response):
        meta_tags = response.xpath("//*[@class='article-meta']/span")
        watch_count_text = ''
        for meta_tag in meta_tags:
            if '观看' in meta_tag.get():
                watch_count_text = meta_tag.css('::text').get().strip('观看()（）')
        return watch_count_text

    def pase_video_page(self, response, category_name, item):
        self.logger.info(f"category_name {category_name}, response url {response.url}")
        iframe_tag = response.xpath("//*[@class='article-content']//iframe")[0]
        article_tags = response.xpath("//*[@class='article-tags']/a")
        like_count_text = response.xpath("//*[@etap='like']/span").css('::text').get()
        watch_count_text = self.parse_watch_count_text(response)
        item["m3u8_page_url"] = iframe_tag.attrib["src"]
        item["id"] = item['m3u8_page_url'].split('/')[-1]
        item["like_count"] = int(like_count_text)
        item["watch_count"] = self.parse_watch_count(watch_count_text)
        video_tags = []
        for article_tag in article_tags:
            video_tags.append(article_tag.css("::text").get())
        item["tags"] = video_tags
        yield scrapy.Request(item['m3u8_page_url'], self.parse_m3u8_page, cb_kwargs={"category_name": category_name, "item": item, "id": item["id"]}, dont_filter=True)

    def get_m3u8_url(self, video_id, token):
        url = urljoin(self.m3u8_base_url, self.m3u8_path_format.format(video_id=video_id))
        url = f'{url}?token={token}'
        return url

    def parse_m3u8_page(self, response, category_name, item, id):
        token_result = self.token_regex.search(response.text)
        if token_result:
            token = token_result.group(1)
            m3u8_url = self.get_m3u8_url(item["id"], token)
            self.logger.info(f'm3u8_url: {m3u8_url}')
            item["file_urls"] = [m3u8_url]
        else:
            self.logger.warning(f'category {category_name}, parse token failed, url {response.url}')
        return item